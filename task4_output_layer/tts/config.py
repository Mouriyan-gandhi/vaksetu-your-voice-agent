"""
TTS Configuration — Language & Voice Registry
==============================================
Maps human-friendly names to Sarvam AI API codes.
"""

# ─── Language Codes (ISO 639-1 + IN suffix) ───────────────────────
LANGUAGES = {
    "hindi":    "hi-IN",
    "kannada":  "kn-IN",
    "english":  "en-IN",
    "bengali":  "bn-IN",
    "gujarati": "gu-IN",
    "malayalam":"ml-IN",
    "marathi":  "mr-IN",
    "odia":     "or-IN",
    "punjabi":  "pa-IN",
    "tamil":    "ta-IN",
    "telugu":   "te-IN",
}

# ─── Voice Personas ───────────────────────────────────────────────
VOICES = {
    "anushka": {
        "speaker": "anushka",
        "gender": "female",
        "use_case": "Default Assistant",
        "description": "Natural, fluent female voice tuned for multilingual conversational output",
        "best_languages": ["hindi", "english", "kannada", "bengali", "tamil", "telugu"],
    },
    "meera": {
        "speaker": "anushka",
        "gender": "female",
        "use_case": "Healthcare Assistant",
        "description": "Warm, empathetic female voice ideal for patient interactions",
        "best_languages": ["hindi", "english"],
    },
    "arjun": {
        "speaker": "aditya",
        "gender": "male",
        "use_case": "Financial Advisor",
        "description": "Professional, confident male voice for business calls",
        "best_languages": ["hindi", "english"],
    },
    "amol": {
        "speaker": "rahul",
        "gender": "male",
        "use_case": "General Assistant",
        "description": "Friendly, clear male voice for general use",
        "best_languages": ["hindi", "english", "marathi"],
    },
    "amruta": {
        "speaker": "anushka",
        "gender": "female",
        "use_case": "Customer Support",
        "description": "Calm, patient female voice for support interactions",
        "best_languages": ["hindi", "english"],
    },
}

# ─── Model Config ─────────────────────────────────────────────────
DEFAULT_MODEL = "bulbul:v3"
DEFAULT_PACE = 0.96
DEFAULT_VOICE = "anushka"
MAX_CHARS_PER_REQUEST = 2500

# ─── API Config ───────────────────────────────────────────────────
SARVAM_TTS_ENDPOINT = "https://api.sarvam.ai/text-to-speech"

# ─── Sample Texts for Testing ────────────────────────────────────
SAMPLE_TEXTS = {
    "hindi": "नमस्ते! मैं आपका एआई असिस्टेंट हूँ। मैं आपकी कैसे मदद कर सकता हूँ?",
    "kannada": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಎಐ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    "english": "Hello! I am your AI assistant. How can I help you today?",
}
