"""
VaakSetu AI Core — RLAIF Reward Engine

Automated quality scoring for completed conversations.
Combines:
  • Programmatic Scorer (40%) — rule-based, instant, no API call
  • LLM Judge Scorer (60%)   — GPT-4o structured evaluation

Usage:
    from task1_ai_core.reward_engine import RewardEngine, ConversationTurn

    engine = RewardEngine()
    turns = [
        ConversationTurn(role="user", content="Mujhe bukhar hai", sentiment_score=0.4, turn_number=1),
        ConversationTurn(role="assistant", content="Kab se hai?", sentiment_score=0.5, turn_number=2),
    ]
    result = await engine.score(turns, domain="healthcare")
    print(result.combined_reward, result.dpo_label)
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

from pydantic import BaseModel, Field

from task1_ai_core.config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    LLM_JUDGE_MODEL,
    REWARD_LLM_WEIGHT,
    REWARD_PROGRAMMATIC_WEIGHT,
    DPO_THRESHOLD,
    IDEAL_TURN_MIN,
    IDEAL_TURN_MAX,
)

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ConversationTurn(BaseModel):
    """A single turn in a conversation."""
    role: str = Field(description="'user' or 'assistant'")
    content: str = Field(description="The spoken/written text")
    sentiment_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Sentiment 0-1")
    turn_number: int = Field(default=0, ge=0, description="Sequential turn number")


class ProgrammaticScores(BaseModel):
    """Rule-based scoring results."""
    turn_efficiency: float = Field(ge=0.0, le=1.0, description="Score based on conversation length")
    sentiment_delta: float = Field(ge=0.0, le=1.0, description="Sentiment improvement start→end")
    resolution_rate: float = Field(ge=0.0, le=1.0, description="1.0 if completed, 0.3 if not")
    content_safety: float = Field(ge=0.0, le=1.0, description="1.0 if no unsafe content")
    average: float = Field(ge=0.0, le=1.0, description="Mean of all programmatic scores")


class LLMJudgeScores(BaseModel):
    """GPT-4o judge scoring results."""
    politeness: int = Field(ge=1, le=5, description="How polite and respectful")
    accuracy: int = Field(ge=1, le=5, description="Correctness, no hallucinations")
    indic_fluency: int = Field(ge=1, le=5, description="Natural Indic language usage")
    policy_compliance: int = Field(ge=1, le=5, description="Follows domain rules")
    resolution_quality: int = Field(ge=1, le=5, description="Achieved conversation goal")
    feedback: str = Field(default="", description="Short improvement suggestion")
    average: float = Field(ge=0.0, le=5.0, description="Mean of the 5 dimension scores")


class RewardResult(BaseModel):
    """Final combined reward output."""
    programmatic: ProgrammaticScores
    llm_judge: LLMJudgeScores
    combined_reward: float = Field(ge=0.0, le=1.0, description="Weighted combined score")
    dpo_label: str = Field(description="'chosen' if ≥ threshold, else 'rejected'")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Reward Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RewardEngine:
    """
    RLAIF scoring engine for conversation quality assessment.

    Combines fast rule-based metrics with an LLM judge for
    comprehensive quality evaluation. Outputs a DPO label
    (chosen/rejected) for preference tuning.
    """

    def __init__(self):
        self._openai_client = None

    # ── Public API ──────────────────────────────────────────────

    async def score(
        self,
        conversation: list[ConversationTurn],
        domain: str = "healthcare",
        is_complete: bool = True,
    ) -> RewardResult:
        """
        Score a completed conversation.

        Args:
            conversation: List of ConversationTurn objects
            domain: Domain ("healthcare" or "financial")
            is_complete: Whether all required fields were collected

        Returns:
            RewardResult with all scores, combined reward, and DPO label
        """
        if not conversation:
            raise ValueError("Cannot score an empty conversation")

        # Score in parallel
        prog_scores = self._programmatic_score(conversation, is_complete)

        try:
            llm_scores = await self._llm_judge_score(conversation, domain)
        except Exception as e:
            logger.error(f"LLM judge failed: {e}. Using default scores.")
            llm_scores = LLMJudgeScores(
                politeness=3, accuracy=3, indic_fluency=3,
                policy_compliance=3, resolution_quality=3,
                feedback=f"LLM judge unavailable: {e}",
                average=3.0,
            )

        # Combine
        combined = self._combine_scores(prog_scores, llm_scores)
        dpo_label = self._assign_dpo_label(combined)

        result = RewardResult(
            programmatic=prog_scores,
            llm_judge=llm_scores,
            combined_reward=round(combined, 4),
            dpo_label=dpo_label,
        )

        logger.info(
            f"Reward scored: combined={combined:.3f}, label={dpo_label}, "
            f"prog_avg={prog_scores.average:.3f}, llm_avg={llm_scores.average:.1f}"
        )

        return result

    # ── Programmatic Scorer (40% weight) ───────────────────────

    def _programmatic_score(
        self,
        conversation: list[ConversationTurn],
        is_complete: bool,
    ) -> ProgrammaticScores:
        """
        Fast rule-based scoring. No API calls.

        Dimensions:
        1. turn_efficiency  — 4-8 turns ideal, score decreases outside
        2. sentiment_delta  — Did sentiment improve over the conversation?
        3. resolution_rate  — Were all required fields collected?
        4. content_safety   — No unsafe / harmful content detected
        """

        # ── Turn efficiency ────────────────────────────────────
        # Count only assistant turns (to match "number of questions asked")
        assistant_turns = sum(1 for t in conversation if t.role == "assistant")
        if IDEAL_TURN_MIN <= assistant_turns <= IDEAL_TURN_MAX:
            turn_efficiency = 1.0
        elif assistant_turns < IDEAL_TURN_MIN:
            # Too few turns — conversation may be incomplete
            turn_efficiency = max(0.3, assistant_turns / IDEAL_TURN_MIN)
        else:
            # Too many turns — agent is being inefficient
            overshoot = assistant_turns - IDEAL_TURN_MAX
            turn_efficiency = max(0.2, 1.0 - (overshoot * 0.1))

        # ── Sentiment delta ────────────────────────────────────
        user_turns = [t for t in conversation if t.role == "user"]
        if len(user_turns) >= 2:
            start_sentiment = user_turns[0].sentiment_score
            end_sentiment = user_turns[-1].sentiment_score
            # Normalized to 0-1: improvement = good, decline = bad
            sentiment_delta = (end_sentiment - start_sentiment + 1.0) / 2.0
        else:
            sentiment_delta = 0.5  # Neutral if not enough data

        # ── Resolution rate ────────────────────────────────────
        resolution_rate = 1.0 if is_complete else 0.3

        # ── Content safety ─────────────────────────────────────
        unsafe_patterns = [
            "die", "kill", "suicide", "harm yourself",
            "marenge", "maar denge", "khatam", "jail",
        ]
        all_text = " ".join(t.content.lower() for t in conversation if t.role == "assistant")
        content_safety = 0.0 if any(p in all_text for p in unsafe_patterns) else 1.0

        # ── Average ────────────────────────────────────────────
        average = (turn_efficiency + sentiment_delta + resolution_rate + content_safety) / 4.0

        return ProgrammaticScores(
            turn_efficiency=round(turn_efficiency, 4),
            sentiment_delta=round(sentiment_delta, 4),
            resolution_rate=round(resolution_rate, 4),
            content_safety=round(content_safety, 4),
            average=round(average, 4),
        )

    # ── LLM Judge Scorer (60% weight) ──────────────────────────

    async def _llm_judge_score(
        self,
        conversation: list[ConversationTurn],
        domain: str,
    ) -> LLMJudgeScores:
        """
        Score conversation using GPT-4o as an LLM judge.
        Returns structured scores per quality dimension.
        """
        import openai

        if self._openai_client is None:
            self._openai_client = openai.OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
            )

        # Format conversation for the judge
        conv_text = self._format_conversation_for_judge(conversation)

        judge_prompt = f"""You are an expert quality evaluator for an AI conversational agent used in the {domain} domain in India.

The agent serves {
    'ASHA health workers documenting patient information' if domain == 'healthcare'
    else 'NBFC loan verification officers collecting payment data'
}.

Evaluate this conversation on 5 dimensions (score each 1-5):

1. **Politeness** — Is the agent warm, respectful, and culturally appropriate?
2. **Accuracy** — Does the agent provide correct information without hallucinations?
3. **Indic Fluency** — Does the agent use natural Hindi/Kannada/Hinglish that matches the user's language?
4. **Policy Compliance** — Does the agent follow rules? (Healthcare: no medical advice. Financial: no threats)
5. **Resolution Quality** — Did the agent effectively collect the required information?

Also provide a brief feedback string (1-2 sentences) suggesting one improvement.

CONVERSATION:
{conv_text}

Respond with ONLY valid JSON in this exact format:
{{
    "politeness": <1-5>,
    "accuracy": <1-5>,
    "indic_fluency": <1-5>,
    "policy_compliance": <1-5>,
    "resolution_quality": <1-5>,
    "feedback": "<1-2 sentence improvement suggestion>"
}}"""

        try:
            response = await asyncio.to_thread(
                self._openai_client.chat.completions.create,
                model=LLM_JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": "You are a strict but fair conversation quality judge. Respond ONLY with valid JSON."},
                    {"role": "user", "content": judge_prompt},
                ],
                temperature=0.1,  # Low temp for consistent scoring
                max_tokens=300,
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON from response (handle markdown code blocks)
            if "```" in content:
                # Extract JSON from code block
                json_match = content.split("```")[1]
                if json_match.startswith("json"):
                    json_match = json_match[4:]
                content = json_match.strip()

            scores = json.loads(content)

            # Validate and clamp scores
            def clamp(val, lo=1, hi=5):
                return max(lo, min(hi, int(val)))

            politeness = clamp(scores.get("politeness", 3))
            accuracy = clamp(scores.get("accuracy", 3))
            indic_fluency = clamp(scores.get("indic_fluency", 3))
            policy_compliance = clamp(scores.get("policy_compliance", 3))
            resolution_quality = clamp(scores.get("resolution_quality", 3))
            feedback = str(scores.get("feedback", "No feedback provided"))

            average = (politeness + accuracy + indic_fluency + policy_compliance + resolution_quality) / 5.0

            return LLMJudgeScores(
                politeness=politeness,
                accuracy=accuracy,
                indic_fluency=indic_fluency,
                policy_compliance=policy_compliance,
                resolution_quality=resolution_quality,
                feedback=feedback,
                average=round(average, 2),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM judge JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM judge API call failed: {e}")
            raise

    # ── Score Combining ────────────────────────────────────────

    def _combine_scores(
        self,
        prog: ProgrammaticScores,
        llm: LLMJudgeScores,
    ) -> float:
        """
        Combine programmatic and LLM scores.
        Formula: (LLM_normalized × 0.6) + (Programmatic_avg × 0.4)
        """
        llm_normalized = llm.average / 5.0  # Scale 1-5 → 0-1
        combined = (llm_normalized * REWARD_LLM_WEIGHT) + (prog.average * REWARD_PROGRAMMATIC_WEIGHT)
        return max(0.0, min(1.0, combined))

    def _assign_dpo_label(self, combined: float) -> str:
        """Assign DPO preference label based on threshold."""
        return "chosen" if combined >= DPO_THRESHOLD else "rejected"

    # ── Helpers ─────────────────────────────────────────────────

    def _format_conversation_for_judge(
        self,
        conversation: list[ConversationTurn],
    ) -> str:
        """Format conversation turns into a readable transcript for the LLM judge."""
        lines = []
        for turn in conversation:
            role_label = "User" if turn.role == "user" else "Agent"
            lines.append(f"[Turn {turn.turn_number}] {role_label}: {turn.content}")
        return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Standalone Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    async def _test():
        engine = RewardEngine()

        # Sample healthcare conversation
        sample_conversation = [
            ConversationTurn(
                role="assistant",
                content="Namaste! Main Aarogya Sahayak hoon. Aapki swasthya jaankari note karne mein madad karunga.",
                sentiment_score=0.6,
                turn_number=1,
            ),
            ConversationTurn(
                role="user",
                content="Mujhe teen din se bukhar hai aur khansi bhi ho rahi hai",
                sentiment_score=0.35,
                turn_number=2,
            ),
            ConversationTurn(
                role="assistant",
                content="Samajh gaya. Aapka naam kya hai?",
                sentiment_score=0.5,
                turn_number=3,
            ),
            ConversationTurn(
                role="user",
                content="Ramesh Kumar, 45 saal, male",
                sentiment_score=0.5,
                turn_number=4,
            ),
            ConversationTurn(
                role="assistant",
                content="Dhanyavaad Ramesh ji. Kya aap koi dawa le rahe hain?",
                sentiment_score=0.6,
                turn_number=5,
            ),
            ConversationTurn(
                role="user",
                content="Haan, paracetamol le raha hoon. Koi allergy nahi hai mujhe.",
                sentiment_score=0.55,
                turn_number=6,
            ),
            ConversationTurn(
                role="assistant",
                content="Theek hai Ramesh ji. Aapki saari jaankari note kar li hai. Dhanyavaad!",
                sentiment_score=0.7,
                turn_number=7,
            ),
            ConversationTurn(
                role="user",
                content="Dhanyavaad, aapne bahut achhi madad ki",
                sentiment_score=0.8,
                turn_number=8,
            ),
        ]

        print(f"\n{'='*60}")
        print("  VaakSetu RLAIF Reward Engine — Test")
        print(f"{'='*60}")
        print(f"\n📝 Scoring a {len(sample_conversation)}-turn healthcare conversation...\n")

        result = await engine.score(sample_conversation, domain="healthcare", is_complete=True)

        print("━━━ Programmatic Scores (40%) ━━━")
        print(f"  Turn Efficiency : {result.programmatic.turn_efficiency:.2f}")
        print(f"  Sentiment Delta : {result.programmatic.sentiment_delta:.2f}")
        print(f"  Resolution Rate : {result.programmatic.resolution_rate:.2f}")
        print(f"  Content Safety  : {result.programmatic.content_safety:.2f}")
        print(f"  Average         : {result.programmatic.average:.2f}")

        print(f"\n━━━ LLM Judge Scores (60%) ━━━")
        print(f"  Politeness       : {result.llm_judge.politeness}/5")
        print(f"  Accuracy         : {result.llm_judge.accuracy}/5")
        print(f"  Indic Fluency    : {result.llm_judge.indic_fluency}/5")
        print(f"  Policy Compliance: {result.llm_judge.policy_compliance}/5")
        print(f"  Resolution       : {result.llm_judge.resolution_quality}/5")
        print(f"  Average          : {result.llm_judge.average:.1f}/5")
        print(f"  Feedback         : {result.llm_judge.feedback}")

        print(f"\n━━━ Combined Result ━━━")
        print(f"  Combined Reward : {result.combined_reward:.4f}")
        print(f"  DPO Label       : {'✅ ' + result.dpo_label if result.dpo_label == 'chosen' else '❌ ' + result.dpo_label}")
        print(f"  Threshold       : {DPO_THRESHOLD}")

        # Print full JSON
        print(f"\n━━━ Full JSON ━━━")
        print(result.model_dump_json(indent=2))

    asyncio.run(_test())
