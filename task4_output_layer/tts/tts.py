"""
Sarvam AI Text-to-Speech Engine
================================
Core TTS module that converts text → natural speech using Sarvam Bulbul v3.
Supports Hindi, Kannada, Indian English, and 8 more Indian languages.

Usage:
    from tts import SarvamTTS
    
    engine = SarvamTTS()
    engine.speak("नमस्ते!", language="hindi", speaker="meera")
"""

import os
import io
import sys
import base64
import time
import requests

from dotenv import load_dotenv

from .config import (
    LANGUAGES,
    VOICES,
    DEFAULT_MODEL,
    DEFAULT_PACE,
    DEFAULT_VOICE,
    MAX_CHARS_PER_REQUEST,
    SARVAM_TTS_ENDPOINT,
)

load_dotenv()


class SarvamTTS:
    """High-level wrapper around the Sarvam AI TTS API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "❌ SARVAM_API_KEY not found!\n"
                "   Set it in your .env file or pass it directly:\n"
                "   engine = SarvamTTS(api_key='your_key_here')"
            )
        self.endpoint = SARVAM_TTS_ENDPOINT
        self.model = DEFAULT_MODEL
        self.headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

    # ─── Core API Call ────────────────────────────────────────────

    def synthesize(
        self,
        text: str,
        language: str = "hindi",
        speaker: str = DEFAULT_VOICE,
        pace: float = DEFAULT_PACE,
        audio_format: str = "wav",
    ) -> bytes:
        """
        Convert text to speech audio bytes.

        Args:
            text: Text to convert (max 2500 chars per call).
            language: Language name (hindi/kannada/english/etc).
            speaker: Voice persona name (meera/arjun/amol/amruta).
            pace: Speech speed (0.5 = slow, 1.0 = normal, 2.0 = fast).
            audio_format: Output format (wav/mp3/aac/opus/flac).

        Returns:
            Raw audio bytes.
        """
        # Resolve language code
        lang_code = LANGUAGES.get(language.lower())
        if not lang_code:
            available = ", ".join(LANGUAGES.keys())
            raise ValueError(
                f"❌ Unknown language '{language}'. Available: {available}"
            )

        # Resolve speaker (fallback to default female voice for natural output)
        speaker_name = (speaker or DEFAULT_VOICE).lower()
        if speaker_name in VOICES:
            speaker_name = VOICES[speaker_name]["speaker"]
        else:
            print(f"⚠️ Unknown voice '{speaker}'. Falling back to '{DEFAULT_VOICE}'.")
            speaker_name = VOICES[DEFAULT_VOICE]["speaker"]

        # Handle long text by chunking
        if len(text) > MAX_CHARS_PER_REQUEST:
            return self._synthesize_long_text(
                text, lang_code, speaker_name, pace, audio_format
            )

        # Build request payload
        payload = {
            # Sarvam cookbook examples use `inputs=[text]` and preprocessing for better fluency.
            "inputs": [text],
            "target_language_code": lang_code,
            "speaker": speaker_name,
            "model": self.model,
            "pace": pace,
            "pitch": 0,
            "loudness": 1.1,
            "speech_sample_rate": 22050,
            "enable_preprocessing": True,
        }

        # Make API call with retry
        audio_bytes = self._api_call_with_retry(payload)
        return audio_bytes

    def _api_call_with_retry(self, payload: dict, max_retries: int = 3) -> bytes:
        """Make API call with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=self.headers,
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()
                    audio_b64 = data.get("audios", [None])[0] or data.get("audio_content")
                    if not audio_b64:
                        raise ValueError("No audio data in API response")
                    return base64.b64decode(audio_b64)

                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    print(f"⏳ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                else:
                    raise requests.exceptions.HTTPError(
                        f"API Error {response.status_code}: {response.text}"
                    )

            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"🔄 Connection error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

        raise RuntimeError("Max retries exceeded for TTS API call")

    def _synthesize_long_text(
        self, text: str, lang_code: str, speaker: str, pace: float, audio_format: str
    ) -> bytes:
        """Split long text into chunks and concatenate audio."""
        chunks = self._split_text(text)
        print(f"📝 Text too long ({len(text)} chars). Split into {len(chunks)} chunks.")

        all_audio = b""
        for i, chunk in enumerate(chunks, 1):
            print(f"   🔊 Processing chunk {i}/{len(chunks)}...")
            payload = {
                "inputs": [chunk],
                "target_language_code": lang_code,
                "speaker": speaker,
                "model": self.model,
                "pace": pace,
                "pitch": 0,
                "loudness": 1.1,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
            }
            audio_bytes = self._api_call_with_retry(payload)
            all_audio += audio_bytes
            time.sleep(0.3)  # Rate limit courtesy delay

        return all_audio

    @staticmethod
    def _split_text(text: str) -> list:
        """
        Intelligently split text at sentence boundaries.
        Prefers splitting at periods, question marks, or exclamation marks.
        """
        chunks = []
        current = ""

        # Split by sentence-ending punctuation
        sentences = []
        temp = ""
        for char in text:
            temp += char
            if char in ".?!।":  # Including Hindi purna viram
                sentences.append(temp.strip())
                temp = ""
        if temp.strip():
            sentences.append(temp.strip())

        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= MAX_CHARS_PER_REQUEST:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    chunks.append(current)
                current = sentence

        if current:
            chunks.append(current)

        return chunks

    # ─── Playback ─────────────────────────────────────────────────

    def speak(
        self,
        text: str,
        language: str = "hindi",
        speaker: str = DEFAULT_VOICE,
        pace: float = DEFAULT_PACE,
    ) -> None:
        """
        Synthesize text and play it through the speakers immediately.
        
        This is the main "type text → hear speech" function.
        """
        try:
            import sounddevice as sd
            from scipy.io import wavfile
        except ImportError:
            print("❌ Audio playback requires: pip install sounddevice scipy")
            print("   Falling back to saving audio file...")
            self.save_audio(text, language, speaker, "output/fallback_output.wav")
            return

        print(f"🎤 Synthesizing [{language}] with voice [{speaker}]...")
        audio_bytes = self.synthesize(text, language, speaker, pace, audio_format="wav")

        # Parse WAV data and play
        try:
            audio_io = io.BytesIO(audio_bytes)
            sample_rate, audio_data = wavfile.read(audio_io)
            print(f"🔊 Playing audio ({len(audio_data)/sample_rate:.1f}s)...")
            sd.play(audio_data, samplerate=sample_rate)
            sd.wait()  # Block until playback finishes
            print("✅ Playback complete!")
        except Exception as e:
            print(f"⚠️  Playback error: {e}")
            print("   Saving to file instead...")
            fallback_path = "output/fallback_output.wav"
            self._save_bytes(audio_bytes, fallback_path)
            print(f"   💾 Saved to {fallback_path}")

    # ─── Save to File ─────────────────────────────────────────────

    def save_audio(
        self,
        text: str,
        language: str = "hindi",
        speaker: str = DEFAULT_VOICE,
        filepath: str = "output/tts_output.wav",
        pace: float = DEFAULT_PACE,
    ) -> str:
        """
        Synthesize text and save the audio to a file.

        Returns:
            The filepath where audio was saved.
        """
        # Determine format from extension
        ext = os.path.splitext(filepath)[1].lstrip(".")
        audio_format = ext if ext in ("wav", "mp3", "aac", "opus", "flac") else "wav"

        print(f"🎤 Synthesizing [{language}] with voice [{speaker}]...")
        audio_bytes = self.synthesize(text, language, speaker, pace, audio_format)

        self._save_bytes(audio_bytes, filepath)
        print(f"💾 Audio saved to: {filepath}")
        return filepath

    @staticmethod
    def _save_bytes(audio_bytes: bytes, filepath: str) -> None:
        """Write raw bytes to file, creating directories if needed."""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

    # ─── Utility ──────────────────────────────────────────────────

    def list_voices(self) -> None:
        """Print available voices and their details."""
        print("\n🎙️  Available Voices:")
        print("=" * 60)
        for name, info in VOICES.items():
            gender_icon = "♀️" if info["gender"] == "female" else "♂️"
            print(f"  {gender_icon}  {name:<10} │ {info['use_case']:<20} │ {info['description']}")
        print("=" * 60)

    def list_languages(self) -> None:
        """Print available languages."""
        print("\n🌍 Available Languages:")
        print("=" * 40)
        for name, code in LANGUAGES.items():
            print(f"  • {name:<12} → {code}")
        print("=" * 40)


# ─── Quick Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    engine = SarvamTTS()
    engine.list_voices()
    engine.list_languages()
    engine.speak("Hello! I am your AI assistant.", language="english", speaker="meera")
