"""
VaakSetu — Live Microphone WebSocket Handler (Rewritten)

Architecture:
  - Browser sends transcribed TEXT (via Web Speech API) — no ASR needed server-side
  - Optionally also receives raw audio for server-side ASR enhancement 
  - LangGraph agent processes text chunks incrementally
  - After "stop", triggers full final summary generation

This avoids all ASR codec/format issues by using the browser's
built-in speech recognition as the primary transcription engine.
"""

import asyncio
import base64
import json
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from task2_backend.database import (
    get_agent,
    create_agent,
    create_session,
    update_session,
    add_message,
)

logger = logging.getLogger("vaaksetu.live_mic")
router = APIRouter(prefix="/api/live", tags=["Live Microphone"])
LIVE_MIC_AGENT_ID = "live-mic"

# ─── Singleton processor (persisted across requests) ───────────────────────
_processor = None


def _get_processor():
    global _processor
    if _processor is None:
        from task1_ai_core.conversation_processor import StreamConversationProcessor
        _processor = StreamConversationProcessor()
    return _processor


# ─── Per-session in-memory state ────────────────────────────────────────────
_sessions: dict[str, dict] = {}


def _get_session(session_id: str, domain: str = "healthcare") -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id": session_id,
            "domain": domain,
            "transcript_chunks": [],
            "narrative": "",
            "structured_data": {},
            "speaker_map": {},
            "is_recording": True,
            "turn_count": 0,
            "db_ready": False,
            "stop_requested": False,
        }
    return _sessions[session_id]


async def _ensure_live_mic_agent(domain: str) -> dict:
    """
    Ensure a dedicated synthetic agent exists for live.html interactions.
    This lets us persist live websocket sessions using the same sessions table.
    """
    existing = await get_agent(LIVE_MIC_AGENT_ID)
    if existing is not None:
        return existing

    payload = {
        "id": LIVE_MIC_AGENT_ID,
        "name": "Live Mic Observer",
        "domain": "Others",
        "customDomain": f"live-{domain}",
        "inputs": ["Voice"],
        "fields": [],
        "prompt": "System agent for live microphone transcript persistence.",
        "greeting": "Live microphone recording session started.",
        "triggers": [],
        "escalation": {},
        "escalation_message": "",
        "default_language": "hi-IN",
    }
    return await create_agent(payload)


async def _persist_live_session_state(session: dict, status: str):
    """
    Persist current live session state into DB session row.
    """
    if not session.get("db_ready"):
        return

    await update_session(
        session["session_id"],
        collected_fields=session.get("structured_data", {}),
        is_complete=bool(session.get("structured_data")),
        turn_count=session.get("turn_count", 0),
        status=status,
        ended_at=datetime.now(timezone.utc).isoformat() if status != "active" else None,
    )


# ─── Optional server-side ASR (best-effort, never crashes the session) ──────
async def _try_server_asr(audio_bytes: bytes, audio_format: str = "webm") -> Optional[str]:
    """
    Try server-side ASR on raw audio bytes.
    Returns transcript string, or None if ASR fails for any reason.
    Never raises — all errors are caught and logged.
    """
    tmp_path = None
    wav_path = None
    try:
        from task1_ai_core.config import SARVAM_API_KEY
        if not SARVAM_API_KEY:
            return None

        # Write incoming bytes to temp file
        with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # Convert to 16kHz WAV using pydub (requires ffmpeg)
        from pydub import AudioSegment
        audio = AudioSegment.from_file(tmp_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        wav_path = tempfile.mktemp(suffix=".wav")
        audio.export(wav_path, format="wav")

        # Call Sarvam STT
        from sarvamai import SarvamAI
        client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

        with open(wav_path, "rb") as f:
            resp = client.speech_to_text.transcribe(
                file=f,
                model="saaras:v3",
                mode="transcribe",
                language_code="unknown",
            )

        transcript = getattr(resp, "transcript", "") or ""
        return transcript.strip() if transcript.strip() else None

    except Exception as e:
        logger.warning(f"Server ASR failed (non-fatal): {type(e).__name__}: {e}")
        return None
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
        if wav_path:
            Path(wav_path).unlink(missing_ok=True)


# ─── Full summary generation using LLM ───────────────────────────────────────
async def _generate_final_summary(transcript_chunks: list[str], domain: str) -> dict:
    """
    Generate a polished final summary from the complete transcript.
    Uses Sarvam-M LLM to produce narrative + structured data.
    """
    if not transcript_chunks:
        return {"narrative": "No transcript captured.", "structured_data": {}}

    full_transcript = "\n".join(
        f"[Chunk {i+1}]: {chunk}" for i, chunk in enumerate(transcript_chunks)
    )

    domain_instructions = {
        "healthcare": (
            "Extract: patient_name, doctor_name, chief_complaint, symptoms (list), "
            "diagnosis, medications (list), treatment_plan, follow_up_date, allergies."
        ),
        "finance": (
            "Extract: client_name, advisor_name, investment_goal, risk_appetite, "
            "products_discussed (list), amounts_mentioned (list), action_items (list), next_steps."
        ),
    }
    extract_instruction = domain_instructions.get(domain, "Extract key entities and action items.")

    prompt = f"""You are an expert medical/financial scribe. 
Analyze the following conversation transcript and provide:
1. A professional third-person narrative summary (3-5 sentences)
2. Structured JSON with extracted fields

Domain: {domain}
{extract_instruction}

Transcript:
{full_transcript}

Respond in this EXACT JSON format:
{{
  "narrative": "...",
  "structured_data": {{
    "field_name": "value"
  }}
}}"""

    try:
        from task1_ai_core.config import SARVAM_API_KEY, SARVAM_CHAT_MODEL, SARVAM_CHAT_BASE_URL
        from openai import OpenAI

        client = OpenAI(
            api_key=SARVAM_API_KEY,
            base_url=SARVAM_CHAT_BASE_URL,
        )

        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model=SARVAM_CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return {
                "narrative": result.get("narrative", ""),
                "structured_data": result.get("structured_data", {}),
            }

    except Exception as e:
        logger.error(f"Final summary LLM call failed: {e}")

    # Fallback: simple join
    return {
        "narrative": f"Conversation captured across {len(transcript_chunks)} segments. "
                     f"Full transcript recorded for review.",
        "structured_data": {"total_chunks": len(transcript_chunks), "domain": domain},
    }


# ─── WebSocket Endpoint ───────────────────────────────────────────────────────
@router.websocket("/stream")
async def live_mic_stream(websocket: WebSocket):
    """
    WebSocket protocol (all messages are JSON strings):

    CLIENT → SERVER:
      {"type": "start", "domain": "healthcare"}
      {"type": "transcript_text", "text": "doctor said the patient has..."}   ← Browser STT
      {"type": "audio_chunk", "data": "<base64>", "format": "webm"}           ← Raw audio (optional)
      {"type": "stop"}

    SERVER → CLIENT:
      {"type": "session_started", "session_id": "..."}
      {"type": "transcript_ack", "text": "...", "chunk_index": N}
      {"type": "agent_update", "narrative": "...", "structured_data": {...}}
      {"type": "processing", "message": "Generating final summary..."}
      {"type": "summary_complete", "transcript": [...], "narrative": "...", "structured_data": {...}}
      {"type": "error", "message": "..."}
    """
    await websocket.accept()
    session_id = f"live-{uuid.uuid4().hex[:8]}"
    session = None

    logger.info(f"[{session_id}] Live mic WebSocket connected")

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "")

            # ── START ──────────────────────────────────────────────
            if msg_type == "start":
                domain = msg.get("domain", "healthcare")
                session = _get_session(session_id, domain)
                try:
                    live_agent = await _ensure_live_mic_agent(domain)
                    await create_session(session_id, live_agent["id"])
                    session["db_ready"] = True
                except Exception as db_err:
                    # Keep websocket usable even if DB persistence fails
                    logger.warning(f"[{session_id}] Failed to initialize DB session: {db_err}")

                await websocket.send_text(json.dumps({
                    "type": "session_started",
                    "session_id": session_id,
                }))
                logger.info(f"[{session_id}] Session started, domain={domain}")

            # ── TRANSCRIPT TEXT (from browser Web Speech API) ──────
            elif msg_type == "transcript_text":
                if not session:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Send {type: start} first.",
                    }))
                    continue

                text = msg.get("text", "").strip()
                if not text:
                    continue

                chunk_index = len(session["transcript_chunks"])
                session["transcript_chunks"].append(text)
                session["turn_count"] = chunk_index + 1

                logger.info(f"[{session_id}] Text chunk {chunk_index}: '{text[:80]}'")

                if session.get("db_ready"):
                    try:
                        await add_message(
                            session_id,
                            "user",
                            text,
                            turn_number=session["turn_count"],
                        )
                    except Exception as db_err:
                        logger.warning(f"[{session_id}] Failed to persist chunk: {db_err}")

                # Acknowledge immediately
                await websocket.send_text(json.dumps({
                    "type": "transcript_ack",
                    "text": text,
                    "chunk_index": chunk_index,
                }))

                # Feed into LangGraph agent (non-blocking)
                try:
                    processor = _get_processor()
                    result = await processor.ingest_chunk(session_id, session["domain"], text)

                    if result.get("status") == "success":
                        session["narrative"] = result.get("narrative", "")
                        session["structured_data"] = result.get("structured_data", {})
                        session["speaker_map"] = result.get("speaker_map", {})

                        await websocket.send_text(json.dumps({
                            "type": "agent_update",
                            "narrative": session["narrative"],
                            "structured_data": session["structured_data"],
                            "speaker_map": session["speaker_map"],
                        }))
                except Exception as e:
                    logger.error(f"[{session_id}] Agent error: {e}", exc_info=True)

            # ── AUDIO CHUNK (optional, for enhanced server-side ASR) ──
            elif msg_type == "audio_chunk":
                if not session:
                    continue

                audio_b64 = msg.get("data", "")
                audio_fmt = msg.get("format", "webm")
                if not audio_b64:
                    continue

                audio_bytes = base64.b64decode(audio_b64)

                # Try server ASR (non-blocking, best-effort)
                async def _process_audio():
                    server_text = await _try_server_asr(audio_bytes, audio_fmt)
                    if server_text:
                        # Only add if meaningfully different from last browser transcript
                        chunks = session.get("transcript_chunks", [])
                        last = chunks[-1] if chunks else ""
                        # Skip if server text is a subset of browser text
                        if server_text.lower() not in last.lower():
                            logger.info(f"[{session_id}] Server ASR enhanced: '{server_text[:60]}'")
                            await websocket.send_text(json.dumps({
                                "type": "transcript_ack",
                                "text": f"[Enhanced] {server_text}",
                                "chunk_index": len(chunks),
                                "source": "server_asr",
                            }))

                asyncio.create_task(_process_audio())

            # ── STOP ────────────────────────────────────────────────
            elif msg_type == "stop":
                if not session:
                    break

                session["is_recording"] = False
                session["stop_requested"] = True
                logger.info(f"[{session_id}] Stop received. Generating final summary...")

                # Notify client we're processing
                await websocket.send_text(json.dumps({
                    "type": "processing",
                    "message": "Generating comprehensive summary...",
                }))

                # Generate final summary using LLM
                summary = await _generate_final_summary(
                    session["transcript_chunks"],
                    session["domain"],
                )

                # Update session
                session["narrative"] = summary.get("narrative", session["narrative"])
                session["structured_data"] = {
                    **session.get("structured_data", {}),
                    **summary.get("structured_data", {}),
                }

                if session.get("db_ready"):
                    try:
                        summary_text = session.get("narrative", "").strip()
                        if summary_text:
                            await add_message(
                                session_id,
                                "assistant",
                                f"[Live Summary] {summary_text}",
                                turn_number=session["turn_count"] + 1,
                            )
                        await _persist_live_session_state(session, status="completed")
                    except Exception as db_err:
                        logger.warning(f"[{session_id}] Failed to persist final summary: {db_err}")

                await websocket.send_text(json.dumps({
                    "type": "summary_complete",
                    "transcript": session["transcript_chunks"],
                    "narrative": session["narrative"],
                    "structured_data": session["structured_data"],
                    "speaker_map": session["speaker_map"],
                }))

                logger.info(f"[{session_id}] Summary sent. Session complete.")
                break

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] Client disconnected")
    except Exception as e:
        logger.error(f"[{session_id}] WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}",
            }))
        except Exception:
            pass
    finally:
        if session and session.get("db_ready") and not session.get("stop_requested"):
            try:
                await _persist_live_session_state(session, status="paused")
            except Exception as db_err:
                logger.warning(f"[{session_id}] Failed to persist paused state: {db_err}")

        # Keep session in memory for later retrieval
        logger.info(f"[{session_id}] Connection closed")
