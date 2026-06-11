"""
VaakSetu Backend — Session & Conversation Routes

Endpoints:
  POST  /api/sessions                — Start a new session for an agent
  POST  /api/sessions/{id}/message   — Send a message and get AI response
  GET   /api/sessions/{id}           — Get full session state + messages
  POST  /api/sessions/{id}/end       — End session, trigger scoring
  POST  /api/transcribe              — ASR: audio bytes → text
"""

import uuid
import logging
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from task2_backend.database import (
    get_agent,
    create_session,
    get_session,
    update_session,
    add_message,
    get_messages,
    list_sessions,
    delete_session,
)

logger = logging.getLogger("vaaksetu.routes.sessions")
router = APIRouter(prefix="/api", tags=["sessions"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Request Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StartSessionRequest(BaseModel):
    agent_id: str


class SendMessageRequest(BaseModel):
    content: str
    input_type: str = "text"  # "text" or "voice"
    language_code: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    status: Optional[str] = None
    is_complete: Optional[bool] = None
    collected_fields: Optional[dict] = None
    ended_at: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Lazy-loaded AI components (avoid import-time failures)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_smart_agent = None
_asr_pipeline = None
_reward_engine = None
_tts_pipeline = None


def _get_agent():
    """Lazy-init the SmartDialogueAgent."""
    global _smart_agent
    if _smart_agent is None:
        from task1_ai_core.agent import SmartDialogueAgent
        _smart_agent = SmartDialogueAgent()
    return _smart_agent


def _get_asr():
    """Lazy-init the ASR pipeline."""
    global _asr_pipeline
    if _asr_pipeline is None:
        from task1_ai_core.asr import ASRPipeline
        _asr_pipeline = ASRPipeline()
    return _asr_pipeline


def _get_reward():
    """Lazy-init the reward engine."""
    global _reward_engine
    if _reward_engine is None:
        from task1_ai_core.reward_engine import RewardEngine
        _reward_engine = RewardEngine()
    return _reward_engine


def _get_tts():
    """Lazy-init the TTS pipeline."""
    global _tts_pipeline
    if _tts_pipeline is None:
        from task1_ai_core.tts import get_tts_pipeline
        _tts_pipeline = get_tts_pipeline()
    return _tts_pipeline


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Routes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/sessions")
async def api_start_session(req: StartSessionRequest):
    """Start a new conversation session for an agent."""
    agent = await get_agent(req.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    session_id = f"s-{uuid.uuid4().hex[:8]}"

    # Create session in DB
    session = await create_session(session_id, req.agent_id)

    # Build agent config and start the AI session
    smart_agent = _get_agent()
    greeting_response = await smart_agent.start_session(
        session_id=session_id,
        agent_config=agent,
    )

    # Save greeting as first message
    await add_message(session_id, "assistant", greeting_response.response, turn_number=0)

    # Synthesise greeting audio (non-blocking; None if Sarvam TTS unavailable)
    greeting_audio_b64 = None
    try:
        from task1_ai_core.tts import detect_language_code
        lang = detect_language_code(greeting_response.response) or agent.get("default_language", "hi-IN")
        greeting_audio_b64 = await _get_tts().synthesise_b64(
            greeting_response.response, language_code=lang
        )
    except Exception as tts_err:
        logger.warning(f"TTS failed for greeting: {tts_err}")

    logger.info(f"Session started: {session_id} for agent {req.agent_id}")
    return {
        "status": "ok",
        "session_id": session_id,
        "greeting": greeting_response.response,
        "greeting_audio": greeting_audio_b64,   # base64 WAV or null
        "missing_fields": greeting_response.missing_fields,
        "agent": agent,
        "language_code": lang,
    }


@router.get("/sessions")
async def api_list_sessions():
    """List all live interaction sessions with agent and message metadata."""
    sessions = await list_sessions()

    enriched = []
    for s in sessions:
        agent = await get_agent(s["agent_id"])
        messages = await get_messages(s["id"])
        enriched.append({
            **s,
            "agent_name": agent["name"] if agent else "Unknown",
            "agent_domain": agent["domain"] if agent else "Unknown",
            "message_count": len(messages),
        })

    return {"status": "ok", "sessions": enriched}


@router.post("/sessions/{session_id}/message")
async def api_send_message(session_id: str, req: SendMessageRequest):
    """Send a user message and get AI response."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is no longer active")

    agent = await get_agent(session["agent_id"])
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Increment turn count
    turn = session["turn_count"] + 1

    # Save user message
    await add_message(session_id, "user", req.content, turn_number=turn)

    # Get AI response
    smart_agent = _get_agent()
    response = await smart_agent.respond(
        session_id=session_id,
        user_input=req.content,
        agent_config=agent,
    )

    # Save assistant message
    await add_message(session_id, "assistant", response.response, turn_number=turn)

    # Update session state
    await update_session(
        session_id,
        collected_fields=response.collected_fields,
        is_complete=response.is_complete,
        turn_count=turn,
    )

    # Synthesise response audio
    response_audio_b64 = None
    lang = agent.get("default_language", "hi-IN")
    try:
        from task1_ai_core.tts import detect_language_code
        detected_lang = detect_language_code(response.response)
        
        # Use detected language if found, otherwise request language, otherwise agent default
        lang = detected_lang or req.language_code or lang
        
        response_audio_b64 = await _get_tts().synthesise_b64(
            response.response, language_code=lang
        )
    except Exception as tts_err:
        logger.warning(f"TTS failed for turn {turn}: {tts_err}")

    logger.info(
        f"Session {session_id} turn {turn}: "
        f"collected={list(response.collected_fields.keys())}, "
        f"complete={response.is_complete}"
    )

    return {
        "status": "ok",
        "response": response.response,
        "response_audio": response_audio_b64,    # base64 WAV or null
        "collected_fields": response.collected_fields,
        "missing_fields": response.missing_fields,
        "is_complete": response.is_complete,
        "is_escalation": response.is_escalation,
        "turn_number": turn,
        "language_code": lang,
    }


@router.get("/sessions/{session_id}")
async def api_get_session(session_id: str):
    """Get full session data including messages."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await get_messages(session_id)
    agent = await get_agent(session["agent_id"])

    return {
        "status": "ok",
        "session": session,
        "messages": messages,
        "agent": agent,
    }


@router.put("/sessions/{session_id}")
async def api_update_session(session_id: str, req: SessionUpdateRequest):
    """Update editable session properties for operations dashboards."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    update_payload = req.model_dump(exclude_none=True)
    updated = await update_session(session_id, **update_payload)
    return {"status": "ok", "session": updated}


@router.delete("/sessions/{session_id}")
async def api_delete_session(session_id: str):
    """Delete a session and all associated messages."""
    deleted = await delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "ok", "message": "Session deleted"}


@router.post("/sessions/{session_id}/end")
async def api_end_session(session_id: str):
    """End a session and trigger RLAIF scoring."""
    session = await get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await get_messages(session_id)
    agent = await get_agent(session["agent_id"])
    now = datetime.now(timezone.utc).isoformat()

    # Run RLAIF scoring
    reward_scores = None
    try:
        from task1_ai_core.reward_engine import RewardEngine, ConversationTurn
        engine = _get_reward()

        turns = [
            ConversationTurn(
                role=m["role"],
                content=m["content"],
                sentiment_score=0.5,  # Simplified — could add real sentiment
                turn_number=m["turn_number"],
            )
            for m in messages
        ]

        if turns:
            result = await engine.score(
                turns,
                domain=agent["domain"] if agent else "general",
                is_complete=session["is_complete"],
            )
            reward_scores = result.model_dump()
            logger.info(f"Session {session_id} scored: {result.combined_reward:.3f} ({result.dpo_label})")
    except Exception as e:
        logger.warning(f"RLAIF scoring failed for {session_id}: {e}")
        reward_scores = {"error": str(e)}

    # Update session as ended
    await update_session(
        session_id,
        status="completed",
        ended_at=now,
        reward_scores=reward_scores,
    )

    return {
        "status": "ok",
        "session": await get_session(session_id),
        "messages": messages,
        "reward_scores": reward_scores,
        "agent": agent,
    }


# ── Standalone TTS endpoint ─────────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    language_code: str = "hi-IN"
    speaker: str = "anushka"


@router.post("/tts")
async def api_tts(req: TTSRequest):
    """
    Synthesise text to speech.
    Returns base64-encoded WAV audio playable in <audio src='data:audio/wav;base64,...'>
    """
    audio_b64 = await _get_tts().synthesise_b64(
        req.text, language_code=req.language_code, speaker=req.speaker
    )
    if audio_b64 is None:
        raise HTTPException(status_code=503, detail="TTS unavailable — check SARVAM_API_KEY")
    return {
        "status": "ok",
        "audio": audio_b64,
        "format": "wav",
        "language_code": req.language_code,
        "speaker": req.speaker,
    }


@router.post("/transcribe")
async def api_transcribe(audio: UploadFile = File(...)):
    """Transcribe audio to text using the ASR pipeline."""
    try:
        asr = _get_asr()
        audio_bytes = await audio.read()

        # Determine format from filename
        ext = Path(audio.filename or "audio.webm").suffix.lstrip(".")
        if ext not in ("wav", "mp3", "webm", "ogg", "m4a"):
            ext = "webm"  # Default for MediaRecorder

        result = await asr.transcribe_bytes(audio_bytes, file_format=ext)

        return {
            "status": "ok",
            "transcript": result.transcript,
            "language_code": result.language_code,
            "confidence": result.confidence,
            "source": result.source,
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

_conv_processor = None
def _get_conversation_processor():
    global _conv_processor
    if _conv_processor is None:
        from task1_ai_core.conversation_processor import ConversationProcessor
        _conv_processor = ConversationProcessor(_get_asr(), _get_agent())
    return _conv_processor

@router.post("/analyze-conversation")
async def api_analyze_conversation(
    agent_id: str = Form(...),
    num_speakers: int = Form(2),
    audio: UploadFile = File(...)
):
    """
    Analyze a multi-speaker audio file.
    Runs diarization, separation, ASR, and context extraction.
    """
    agent = await get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    try:
        # Save uploaded file temporarily for pyannote and pydub to process
        ext = Path(audio.filename or "audio.wav").suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        processor = _get_conversation_processor()
        result = await processor.process_conversation(tmp_path, agent, num_speakers)
        
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return {
            "status": "ok",
            "data": result
        }
    except Exception as e:
        logger.error(f"Conversation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
