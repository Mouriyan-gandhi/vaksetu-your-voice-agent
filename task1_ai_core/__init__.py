"""
VaakSetu AI Core — Task 1 Module

Three sub-modules:
  • asr          — Speech-to-Text (Sarvam STT + IndicWhisper fallback)
  • agent        — Dialogue Agent (Sarvam-M LLM + Redis memory + YAML config)
  • reward_engine — RLAIF Scoring (Programmatic + GPT-4o LLM Judge)
"""

from task1_ai_core.config import validate_config

__all__ = [
    "asr",
    "agent",
    "reward_engine",
    "config",
]

# Run config validation on import — print warnings if keys are missing
_warnings = validate_config()
if _warnings:
    import sys
    for w in _warnings:
        print(w, file=sys.stderr)
