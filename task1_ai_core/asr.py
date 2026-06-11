"""
VaakSetu AI Core — Automatic Speech Recognition (ASR) Pipeline

Primary:  Sarvam STT API (saaras:v3) — cloud, fast, Indic-first
Fallback: AI4Bharat IndicWhisper     — local, offline, HuggingFace

Usage:
    from task1_ai_core.asr import ASRPipeline, TranscriptionResult

    pipeline = ASRPipeline()
    result = await pipeline.transcribe("audio.wav")
    print(result.transcript, result.language_code, result.confidence)
"""

from __future__ import annotations

import asyncio
import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from task1_ai_core.config import (
    SARVAM_API_KEY,
    SARVAM_STT_MODEL,
    SARVAM_STT_MODE,
)

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TranscriptionResult(BaseModel):
    """Result of an ASR transcription."""
    transcript: str = Field(description="Transcribed text from the audio")
    language_code: str = Field(default="unknown", description="BCP-47 language code (e.g., hi-IN)")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    source: str = Field(default="sarvam", description="Which engine produced this: 'sarvam' or 'indicwhisper'")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ASR Pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ASRPipeline:
    """
    Speech-to-text pipeline with automatic fallback.

    1. Tries Sarvam STT API (saaras:v3) — fast, cloud-based, Indic-first
    2. On failure → falls back to IndicWhisper (local HuggingFace model)
    """

    def __init__(self):
        self._sarvam_client = None
        self._indicwhisper_pipe = None  # Lazy-loaded only if needed

    # ── Public API ──────────────────────────────────────────────

    async def transcribe(
        self,
        audio_path: str,
        language_code: str = "unknown",
    ) -> TranscriptionResult:
        """
        Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file (WAV, MP3, etc.)
            language_code: BCP-47 language hint (e.g., "hi-IN"). Use "unknown" for auto-detect.

        Returns:
            TranscriptionResult with transcript, language, confidence, and source.
        """
        audio_path = str(Path(audio_path).resolve())

        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Ensure WAV format for best compatibility
        wav_path = self._ensure_wav_format(audio_path)

        # Try Sarvam STT first
        if SARVAM_API_KEY:
            try:
                result = await asyncio.to_thread(
                    self._transcribe_sarvam, wav_path, language_code
                )
                logger.info(f"Sarvam STT success: '{result.transcript[:50]}...'")
                return result
            except Exception as e:
                logger.warning(f"Sarvam STT failed: {e}. Falling back to IndicWhisper.")
        else:
            logger.warning("SARVAM_API_KEY not set. Using IndicWhisper fallback.")

        # Fallback to IndicWhisper
        try:
            result = await asyncio.to_thread(
                self._transcribe_indicwhisper, wav_path
            )
            logger.info(f"IndicWhisper success: '{result.transcript[:50]}...'")
            return result
        except Exception as e:
            logger.error(f"IndicWhisper also failed: {e}")
            raise RuntimeError(f"All ASR engines failed. Last error: {e}") from e

    async def transcribe_bytes(
        self,
        audio_bytes: bytes,
        language_code: str = "unknown",
        file_format: str = "wav",
    ) -> TranscriptionResult:
        """
        Transcribe audio from raw bytes (e.g., from WebSocket stream).

        Args:
            audio_bytes: Raw audio data.
            language_code: BCP-47 language hint.
            file_format: Audio format extension (wav, mp3, etc.)

        Returns:
            TranscriptionResult
        """
        # Write bytes to a temp file and transcribe
        with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            return await self.transcribe(tmp_path, language_code)
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)

    # ── Sarvam STT (Primary) ───────────────────────────────────

    def _transcribe_sarvam(
        self,
        audio_path: str,
        language_code: str = "unknown",
    ) -> TranscriptionResult:
        """
        Transcribe using Sarvam STT API via the official SDK.
        Model: saaras:v3 with transcribe mode.
        """
        from sarvamai import SarvamAI
        from sarvamai.core.api_error import ApiError

        if self._sarvam_client is None:
            self._sarvam_client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

        try:
            with open(audio_path, "rb") as audio_file:
                response = self._sarvam_client.speech_to_text.transcribe(
                    file=audio_file,
                    model=SARVAM_STT_MODEL,
                    mode=SARVAM_STT_MODE,
                    language_code=language_code,
                )

            # Extract fields from response
            transcript = response.transcript if hasattr(response, 'transcript') else str(response)
            detected_lang = getattr(response, 'language_code', None) or language_code
            lang_probability = getattr(response, 'language_probability', None) or 0.95

            return TranscriptionResult(
                transcript=transcript.strip(),
                language_code=detected_lang if detected_lang else "unknown",
                confidence=float(lang_probability) if lang_probability else 0.95,
                source="sarvam",
            )

        except ApiError as e:
            raise RuntimeError(
                f"Sarvam STT API error (HTTP {e.status_code}): {e.body}"
            ) from e

    # ── IndicWhisper (Fallback) ─────────────────────────────────

    def _transcribe_indicwhisper(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe using AI4Bharat IndicWhisper via HuggingFace transformers.
        Downloads the model on first use (~1.5GB).
        """
        import torch
        from transformers import pipeline as hf_pipeline

        if self._indicwhisper_pipe is None:
            logger.info("Loading IndicWhisper model (first time may take a few minutes)...")
            from task1_ai_core.config import HF_TOKEN

            device = 0 if torch.cuda.is_available() else -1
            self._indicwhisper_pipe = hf_pipeline(
                "automatic-speech-recognition",
                model="ai4bharat/indicwhisper-hindi",
                device=device,
                chunk_length_s=30,
                token=HF_TOKEN,
            )
            logger.info(f"IndicWhisper loaded on {'GPU' if device == 0 else 'CPU'}")

        result = self._indicwhisper_pipe(audio_path)

        transcript = result.get("text", "").strip() if isinstance(result, dict) else str(result).strip()

        return TranscriptionResult(
            transcript=transcript,
            language_code="hi-IN",  # IndicWhisper Hindi model
            confidence=0.85,        # No confidence score from this model
            source="indicwhisper",
        )

    # ── Audio Pre-processing ────────────────────────────────────

    def _ensure_wav_format(self, audio_path: str) -> str:
        """
        Ensure the audio file is in 16kHz mono WAV format.
        If it already is, returns the same path.
        If not, converts using pydub and returns a temp file path.
        """
        path = Path(audio_path)

        # If already WAV, check sample rate with soundfile
        if path.suffix.lower() == ".wav":
            try:
                import soundfile as sf
                info = sf.info(audio_path)
                if info.samplerate == 16000 and info.channels == 1:
                    return audio_path  # Already good
            except Exception:
                pass  # Fall through to conversion

        # Convert using pydub
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            # Write to temp file
            out_path = tempfile.mktemp(suffix=".wav")
            audio.export(out_path, format="wav")
            return out_path

        except Exception as e:
            logger.warning(f"Audio conversion failed: {e}. Using original file.")
            return audio_path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Standalone Test
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    async def _test():
        pipeline = ASRPipeline()

        if len(sys.argv) > 1:
            # Transcribe a provided audio file
            audio_file = sys.argv[1]
            print(f"\n🎤 Transcribing: {audio_file}")
            result = await pipeline.transcribe(audio_file)
        else:
            # Record from microphone using sounddevice
            print("\n🎤 Recording 5 seconds from microphone...")
            import sounddevice as sd
            import soundfile as sf

            samplerate = 16000
            duration = 5
            print("   Speak now!")
            audio_data = sd.rec(
                int(samplerate * duration),
                samplerate=samplerate,
                channels=1,
                dtype="int16",
            )
            sd.wait()
            print("   Recording complete.")

            # Save to temp WAV
            tmp_path = tempfile.mktemp(suffix=".wav")
            sf.write(tmp_path, audio_data, samplerate)
            result = await pipeline.transcribe(tmp_path)
            Path(tmp_path).unlink(missing_ok=True)

        print(f"\n📝 Transcript : {result.transcript}")
        print(f"🌐 Language   : {result.language_code}")
        print(f"📊 Confidence : {result.confidence:.2f}")
        print(f"🔧 Source     : {result.source}")

    asyncio.run(_test())
