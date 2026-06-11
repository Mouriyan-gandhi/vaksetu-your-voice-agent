"""
VaakSetu AI Core — Smart Dialogue Agent (v2)

Upgraded from rigid form-filling to intelligent conversation:
  • LLM-based field extraction (via SmartExtractor)
  • Context-aware: skips collected fields, handles null/unknown
  • Dynamic config: accepts agent config dicts (from DB), not just YAML
  • Multi-field awareness: extracts all info from a single message
  • Natural follow-ups: asks contextual questions, not rigid field prompts

Usage:
    from task1_ai_core.agent import SmartDialogueAgent, AgentResponse

    agent = SmartDialogueAgent()
    greeting = await agent.start_session("s-001", agent_config={...})
    response = await agent.respond("s-001", "Main Ramesh hoon, 45 saal", agent_config={...})
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from task1_ai_core.config import (
    SARVAM_API_KEY,
    SARVAM_CHAT_MODEL,
    SARVAM_CHAT_BASE_URL,
    SARVAM_CHAT_TEMPERATURE,
    SARVAM_CHAT_MAX_TOKENS,
    REDIS_URL,
    CONFIGS_DIR,
    MAX_CONVERSATION_TURNS,
)
from task1_ai_core.smart_extractor import SmartExtractor

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DomainConfig(BaseModel):
    """Parsed YAML domain configuration (legacy support)."""
    domain: str
    agent_name: str
    default_language: str
    greeting: str
    required_fields: list[str]
    system_prompt: str
    escalation_triggers: list[str] = []
    escalation_message: str = ""


class AgentResponse(BaseModel):
    """Response from the dialogue agent."""
    response: str = Field(description="Agent's natural language reply")
    collected_fields: dict[str, Any] = Field(default_factory=dict, description="Fields collected so far")
    missing_fields: list[str] = Field(default_factory=list, description="Fields still needed")
    is_complete: bool = Field(default=False, description="True when all required fields are collected")
    is_escalation: bool = Field(default=False, description="True if escalation was triggered")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Smart Dialogue Agent (v2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SmartDialogueAgent:
    """
    Intelligent multi-turn conversational agent powered by Sarvam-M LLM.

    Improvements over v1:
    - Accepts dynamic agent config from DB (not just YAML files)
    - Uses LLM for field extraction instead of regex
    - Context-aware system prompt that adapts per turn
    - Handles multi-field inputs and null/unknown responses
    """

    def __init__(self):
        self._session_state: dict[str, dict] = {}
        self._history: dict[str, list[dict]] = {}
        self._llm = None
        self._extractor = SmartExtractor()

    # ── LLM Setup ──────────────────────────────────────────────

    def _get_llm(self):
        """Lazy-initialize the LangChain ChatOpenAI pointed at Sarvam."""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=SARVAM_CHAT_MODEL,
                temperature=SARVAM_CHAT_TEMPERATURE,
                max_tokens=4096,  # Sarvam-M uses reasoning tokens, needs headroom
                api_key=SARVAM_API_KEY,
                base_url=SARVAM_CHAT_BASE_URL,
            )
            logger.info(f"LLM initialized: {SARVAM_CHAT_MODEL} @ {SARVAM_CHAT_BASE_URL}")
        return self._llm

    # ── Session Management ─────────────────────────────────────

    async def start_session(
        self,
        session_id: str,
        agent_config: dict,
    ) -> AgentResponse:
        """
        Initialize a new conversation session with a dynamic agent config.
        Returns the greeting message.
        """
        fields = agent_config.get("fields", [])
        greeting = agent_config.get("greeting", "")

        if not greeting:
            name = agent_config.get("name", "Assistant")
            greeting = f"Namaste! Main {name} hoon. Aapki kaise madad kar sakta hoon?"

        # Initialize session state
        self._session_state[session_id] = {
            "agent_config": agent_config,
            "collected_fields": {},
            "turn_count": 0,
            "null_fields": [],  # Fields user explicitly doesn't know
        }
        self._history[session_id] = []

        return AgentResponse(
            response=greeting,
            collected_fields={},
            missing_fields=fields.copy(),
            is_complete=False,
        )

    # ── Core Respond ───────────────────────────────────────────

    async def respond(
        self,
        session_id: str,
        user_input: str,
        agent_config: dict,
    ) -> AgentResponse:
        """
        Process one conversation turn with intelligent field extraction.

        Flow:
        1. Check for escalation triggers
        2. Extract fields from user input using LLM
        3. Build context-aware system prompt
        4. Call Sarvam-M LLM for response generation
        5. Return structured response with field tracking
        """
        session = self._get_or_create_session(session_id, agent_config)
        collected = session["collected_fields"]
        null_fields = session["null_fields"]
        session["turn_count"] += 1

        fields = agent_config.get("fields", [])
        triggers = agent_config.get("triggers", [])
        escalation_msg = agent_config.get("escalation_message", "")

        # ── 1. Escalation check ────────────────────────────────
        if self._check_escalation(user_input, triggers):
            esc_response = escalation_msg or "This seems urgent. Let me connect you with a human agent."
            return AgentResponse(
                response=esc_response,
                collected_fields=collected,
                missing_fields=self._get_missing(fields, collected, null_fields),
                is_complete=False,
                is_escalation=True,
            )

        # ── 2. Run extraction + response LLM calls IN PARALLEL ───
        #    This halves total latency (from ~60s to ~30s).
        #    The response prompt uses pre-extraction state, which is fine
        #    because the LLM sees the user message in conversation history.
        conversation_context = self._format_history(session_id)

        # Build response prompt with current state (pre-extraction)
        missing_before = self._get_missing(fields, collected, null_fields)
        system_prompt = self._build_smart_prompt(agent_config, collected, missing_before, null_fields)
        messages = self._build_messages(system_prompt, session_id, user_input)

        # Define both async tasks
        async def _extract():
            try:
                return await self._extractor.extract_fields(
                    user_message=user_input,
                    required_fields=fields,
                    already_collected=collected,
                    conversation_context=conversation_context,
                )
            except Exception as e:
                logger.warning(f"Extraction failed: {e}. Continuing without extraction.")
                return {}

        async def _respond():
            try:
                llm = self._get_llm()
                response = await asyncio.to_thread(llm.invoke, messages)
                raw_content = response.content
                logger.info(f"🤖 [RAW LLM RESPONSE]: {raw_content!r}")
                stripped = self._strip_think_tags(raw_content)
                logger.info(f"🤖 [STRIPPED LLM RESPONSE]: {stripped!r}")
                return stripped
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                return "Maaf kijiye, mujhe abhi thodi technical problem aa rahi hai. Kya aap dobara keh sakte hain?"

        # Run BOTH LLM calls at the same time
        new_fields, agent_text = await asyncio.gather(_extract(), _respond())

        # ── 3. Post-process extraction results ─────────────────
        for field, value in list(new_fields.items()):
            if value == "__NULL__":
                if field not in null_fields:
                    null_fields.append(field)
                del new_fields[field]

        collected.update(new_fields)
        session["collected_fields"] = collected

        # ── 4. Store turn in history ───────────────────────────
        self._history.setdefault(session_id, [])
        self._history[session_id].append({"role": "user", "content": user_input})
        self._history[session_id].append({"role": "assistant", "content": agent_text})

        # ── 5. Check completion ────────────────────────────────
        missing = self._get_missing(fields, collected, null_fields)
        is_complete = len(missing) == 0

        return AgentResponse(
            response=agent_text,
            collected_fields=collected,
            missing_fields=missing,
            is_complete=is_complete,
        )

    # ── Smart System Prompt ────────────────────────────────────

    def _build_smart_prompt(
        self,
        config: dict,
        collected: dict[str, Any],
        missing: list[str],
        null_fields: list[str],
    ) -> str:
        """Build an intelligent, context-aware system prompt."""
        agent_name = config.get("name", "Assistant")
        domain = config.get("customDomain") or config.get("domain", "general")
        custom_prompt = config.get("prompt", "")

        collected_str = "\n".join(f"  • {k}: {v}" for k, v in collected.items()) if collected else "  None yet."
        missing_str = "\n".join(f"  • {f}" for f in missing) if missing else "  All collected!"
        null_str = "\n".join(f"  • {f}" for f in null_fields) if null_fields else "  None."

        base_prompt = f"""You are {agent_name}, an intelligent multilingual conversational assistant for the {domain} domain.

{custom_prompt}

═══ CORE BEHAVIOR RULES ═══

1. LANGUAGE & TONE:
   - Match the user's language EXACTLY. If they speak Hindi, respond in Hindi. If they speak English, respond in English.
   - If the user is bilingual or mixes languages (like Hinglish/code-switching), give your response in a bilingual/mixed form just like they did!
   - Talk exactly like a LIVE, dynamic, and empathetic human person speaking on a voice call. Use a highly conversational and natural tone. DO NOT sound robotic.

2. ASKING FOR INFORMATION:
   - If you need the user to provide missing information or need anything to do your task, ASK FOR IT naturally embedded in your conversation.
   - Ask ONE question at a time. Keep responses to 1-2 short sentences so it's easy to hear.
   - If the user provides multiple pieces of information at once, acknowledge them before moving on.

3. SMART FIELD COLLECTION:
   - DO NOT ask for fields that are already collected.
   - If the user says "I don't know" or "pata nahi" for something, acknowledge it and move on. Do NOT keep asking the same thing.
   - Pick the most natural next field to ask about based on conversation flow, not a rigid order.

4. HANDLING VAGUE/PARTIAL ANSWERS:
   - If the answer is vague, gently ask a clarifying question.
   - If the user gives an irrelevant answer, politely redirect them.

═══ CURRENT STATE ═══

Fields already collected:
{collected_str}

Fields still needed:
{missing_str}

Fields user doesn't know (skip these):
{null_str}

═══ YOUR TASK ═══
Based on the conversation so far, naturally collect the next missing field. When all fields are collected, provide a warm summary and closing.
"""
        return base_prompt

    # ── Message Building ───────────────────────────────────────

    def _build_messages(
        self,
        system_prompt: str,
        session_id: str,
        user_input: str,
    ) -> list:
        """Build the full message list for the LLM call."""
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history (last N turns)
        history = self._history.get(session_id, [])
        recent = history[-(MAX_CONVERSATION_TURNS * 2):]
        for msg in recent:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Current user input
        messages.append(HumanMessage(content=user_input))
        return messages

    # ── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        """Strip <think>...</think> reasoning tokens from Sarvam-M responses robustly."""
        import re
        # First, strip fully closed think tags
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        # If there is a dangling <think> tag that wasn't closed, strip everything after it
        if "<think>" in cleaned:
            cleaned = cleaned.split("<think>")[0]
        cleaned = cleaned.strip()
        # Fallback if the model only generated thinking and no user-facing response
        if not cleaned and text.strip():
            logging.getLogger(__name__).warning("LLM response contained only reasoning. Returning fallback response.")
            return "Kripya mujhe aur batayein, main sun raha hoon."
        return cleaned

    def _get_or_create_session(self, session_id: str, agent_config: dict) -> dict:
        """Get existing session state or create one."""
        if session_id not in self._session_state:
            self._session_state[session_id] = {
                "agent_config": agent_config,
                "collected_fields": {},
                "turn_count": 0,
                "null_fields": [],
            }
        return self._session_state[session_id]

    def _get_missing(
        self,
        fields: list[str],
        collected: dict[str, Any],
        null_fields: list[str],
    ) -> list[str]:
        """Return fields not yet collected and not marked as null."""
        return [f for f in fields if f not in collected and f not in null_fields]

    def _check_escalation(self, user_input: str, triggers: list[str]) -> bool:
        """Check if user input contains escalation trigger keywords."""
        if not triggers:
            return False
        text_lower = user_input.lower()
        return any(trigger.lower() in text_lower for trigger in triggers)

    def _format_history(self, session_id: str) -> str:
        """Format conversation history as text for context."""
        history = self._history.get(session_id, [])
        lines = []
        for msg in history[-10:]:
            role = "User" if msg["role"] == "user" else "Agent"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def get_conversation_history(self, session_id: str) -> list[dict]:
        """Return the full conversation history for a session."""
        return self._history.get(session_id, [])

    def get_session_state(self, session_id: str) -> dict | None:
        """Return the session state."""
        return self._session_state.get(session_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Legacy DialogueAgent (preserved for backward compat)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Keep the old class name as an alias for any code importing it
DialogueAgent = SmartDialogueAgent
