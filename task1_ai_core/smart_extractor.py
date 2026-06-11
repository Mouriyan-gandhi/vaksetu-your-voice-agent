"""
VaakSetu AI Core — LLM-Based Smart Field Extractor

Instead of regex heuristics, this module uses the Sarvam-M LLM itself
to extract structured field values from natural conversation text.

Handles:
  • Multi-field extraction ("I'm Ramesh, 45 years old, male")
  • Null/unknown detection ("Pata nahi", "I don't know")
  • Vague/partial values that need follow-up
  • Code-mixed Hinglish/Kannada inputs
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from task1_ai_core.config import (
    SARVAM_API_KEY,
    SARVAM_CHAT_MODEL,
    SARVAM_CHAT_BASE_URL,
)

logger = logging.getLogger(__name__)


class SmartExtractor:
    """
    LLM-powered field extraction engine.

    Given a user message and a list of required fields, uses the LLM
    to identify which fields the user has provided values for.
    """

    def __init__(self):
        self._llm = None

    def _get_llm(self):
        """Lazy-initialize the LLM for extraction."""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=SARVAM_CHAT_MODEL,
                temperature=0.1,  # Low temp for consistent extraction
                max_tokens=4096,  # Sarvam-M uses reasoning tokens
                api_key=SARVAM_API_KEY,
                base_url=SARVAM_CHAT_BASE_URL,
            )
        return self._llm

    async def extract_fields(
        self,
        user_message: str,
        required_fields: list[str],
        already_collected: dict[str, Any],
        conversation_context: str = "",
    ) -> dict[str, Any]:
        """
        Extract field values from a user message using LLM.

        Args:
            user_message: The latest user input
            required_fields: List of field names to look for
            already_collected: Fields already collected (to avoid re-extraction)
            conversation_context: Recent conversation for context

        Returns:
            Dict of newly extracted field → value pairs.
            Values can be strings or "__NULL__" for explicitly unknown answers.
        """
        missing_fields = [f for f in required_fields if f not in already_collected]

        if not missing_fields:
            return {}

        extraction_prompt = f"""You are a precise data extraction engine. Your job is to extract structured field values from a user's conversational message.

The user may speak in Hindi, English, Hinglish (mixed), Kannada, or any Indian language. Extract the values regardless of language.

FIELDS TO EXTRACT (only extract these):
{json.dumps(missing_fields, indent=2)}

USER MESSAGE: "{user_message}"

RECENT CONVERSATION CONTEXT:
{conversation_context[-500:] if conversation_context else "No prior context."}

RULES:
1. Only extract fields that the user CLEARLY provides in this message.
2. If the user says "I don't know", "pata nahi", "nahi pata", or similar for a field, set its value to "__NULL__".
3. If a field is not mentioned at all, DO NOT include it in the output.
4. Return ONLY valid JSON with field names as keys and extracted values as strings.
5. Keep values concise and clean (e.g., "Ramesh Kumar" not "mera naam Ramesh Kumar hai").
6. For numeric fields like age, extract just the number as a string.

RESPOND WITH ONLY A JSON OBJECT. No explanation, no markdown, no code blocks.
Example: {{"patient_name": "Ramesh Kumar", "age": "45", "gender": "male"}}
If nothing is extractable, return: {{}}"""

        try:
            from langchain_core.messages import HumanMessage

            llm = self._get_llm()
            response = await asyncio.to_thread(
                llm.invoke,
                [HumanMessage(content=extraction_prompt)]
            )

            content = response.content.strip()

            # Strip <think>...</think> reasoning tokens from Sarvam-M
            import re
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

            # Robust JSON extraction using regex
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                try:
                    extracted = json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode extracted JSON block: {json_match.group()}")
                    extracted = {}
            else:
                logger.warning(f"No JSON block found in extraction response: {content[:100]}")
                extracted = {}

            # Filter to only valid fields
            valid_extracted = {}
            for field, value in extracted.items():
                if field in missing_fields and value:
                    valid_extracted[field] = value

            if valid_extracted:
                logger.info(f"Extracted fields: {list(valid_extracted.keys())}")

            return valid_extracted

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error in extraction: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Smart extraction failed: {e}. Returning empty.")
            return {}
