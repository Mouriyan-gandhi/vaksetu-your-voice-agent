"""
Twilio Webhook Server
======================
Flask server that handles Twilio voice call webhooks.
Uses the real SmartDialogueAgent to provide interactive conversations.
"""

import os
import sys
import asyncio
import logging
import yaml
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

# Add project root so that task1_ai_core can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from task1_ai_core.agent import SmartDialogueAgent

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vaaksetu.webhook_server")

# Global dialogue agent instance
dialogue_agent = SmartDialogueAgent()

DEFAULT_LANGUAGE = os.getenv("CALL_LANGUAGE", "hindi")

VOICE_MAPPING = {
    "hi-IN": ("Polly.Aditi", "hi-IN"),
    "en-IN": ("Polly.Aditi", "en-IN"),
    "ta-IN": ("Polly.Madhur", "ta-IN"),
    "te-IN": ("Polly.Gita", "te-IN"),
    "kn-IN": ("Polly.Kajal", "kn-IN"),
    "bn-IN": ("Google.bn-IN-Standard-A", "bn-IN"),
}

def load_agent_config():
    """Load the healthcare agent configuration from YAML."""
    yaml_path = os.path.join(PROJECT_ROOT, "configs", "healthcare.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)
        
    return {
        "name": yaml_config.get("agent_name", "Aarogya Sahayak"),
        "domain": yaml_config.get("domain", "healthcare"),
        "fields": yaml_config.get("required_fields", []),
        "greeting": yaml_config.get("greeting", ""),
        "prompt": yaml_config.get("system_prompt", ""),
        "triggers": yaml_config.get("escalation_triggers", []),
        "escalation_message": yaml_config.get("escalation_message", ""),
    }

# ─── Routes ───────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Interactive Voice Agent Webhook",
        "endpoints": ["/voice", "/gather", "/status"],
    }


@app.route("/voice", methods=["POST"])
def voice_handler():
    """
    Initial call handler — called when the recipient answers.
    Starts the session with the AI agent and plays the greeting.
    """
    response = VoiceResponse()
    call_sid = request.form.get("CallSid", "unknown")
    lang = request.args.get("lang", DEFAULT_LANGUAGE)

    # Resolve agent config
    agent_config = load_agent_config()

    # Start the session in a synchronous event loop wrapper
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        agent_res = loop.run_until_complete(dialogue_agent.start_session(call_sid, agent_config))
    finally:
        loop.close()

    greeting = agent_res.response

    # Dynamic language detection for greeting
    from task1_ai_core.tts import detect_language_code
    detected_lang = detect_language_code(greeting)
    voice_name, tts_lang = VOICE_MAPPING.get(detected_lang, ("Polly.Aditi", detected_lang))

    gather = Gather(
        input="speech",
        action=f"/gather?lang={tts_lang}",
        method="POST",
        language=tts_lang,
        speech_timeout="auto",
        timeout=10,
        barge_in=True,
    )
    gather.say(greeting, voice=voice_name, language=tts_lang)
    response.append(gather)

    # Fallback if silence
    response.say("Mujhe kuch sunayi nahi diya. Kripya dobara phone karein.", voice=voice_name, language=tts_lang)
    response.hangup()

    logger.info(f"📞 [VOICE] Call {call_sid[:12]} answered. Initialized Aarogya Sahayak session in {tts_lang}.")
    return Response(str(response), mimetype="text/xml")


@app.route("/gather", methods=["POST"])
def gather_handler():
    """
    Handles the gathered speech input from the caller.
    Submits user utterance to the AI brain and speaks back the response.
    """
    response = VoiceResponse()
    call_sid = request.form.get("CallSid", "unknown")
    speech_result = request.form.get("SpeechResult", "")
    confidence = request.form.get("Confidence", "0.0")
    
    current_lang = request.args.get("lang", "hi-IN")

    logger.info(f"🎙️ [GATHER] Speech received for {call_sid[:12]}: '{speech_result}' (Confidence: {confidence}, Lang: {current_lang})")

    agent_config = load_agent_config()

    if speech_result.strip():
        # Get response from dialogue agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            agent_res = loop.run_until_complete(dialogue_agent.respond(call_sid, speech_result, agent_config))
        finally:
            loop.close()

        ai_response = agent_res.response
        logger.info(f"🧠 [AGENT RESPONSE]: '{ai_response}'")

        # Dynamic language detection for response
        from task1_ai_core.tts import detect_language_code
        detected_lang = detect_language_code(ai_response)
        voice_name, tts_lang = VOICE_MAPPING.get(detected_lang, ("Polly.Aditi", detected_lang))

        if agent_res.is_escalation or agent_res.is_complete:
            response.say(ai_response, voice=voice_name, language=tts_lang)
            response.hangup()
            logger.info(f"🏁 [CALL FINISHED] Escalated or Completed. Hanging up.")
        else:
            gather = Gather(
                input="speech",
                action=f"/gather?lang={tts_lang}",
                method="POST",
                language=tts_lang,
                speech_timeout="auto",
                timeout=10,
                barge_in=True,
            )
            gather.say(ai_response, voice=voice_name, language=tts_lang)
            response.append(gather)
    else:
        # Silence fallback
        voice_name, fallback_lang = VOICE_MAPPING.get(current_lang, ("Polly.Aditi", current_lang))
        response.say("Mujhe sunai nahi diya. Aapse nivedan hai ki dobara kahein.", voice=voice_name, language=fallback_lang)
        response.redirect("/voice")

    return Response(str(response), mimetype="text/xml")


@app.route("/status", methods=["POST"])
def status_callback():
    """
    Twilio status callback — logs call status changes.
    """
    call_sid = request.form.get("CallSid", "unknown")
    call_status = request.form.get("CallStatus", "unknown")
    duration = request.form.get("CallDuration", "0")

    status_icons = {
        "initiated": "🟡",
        "ringing": "🔔",
        "in-progress": "🟢",
        "completed": "✅",
        "busy": "🔴",
        "no-answer": "⚪",
        "failed": "❌",
        "canceled": "🚫",
    }
    icon = status_icons.get(call_status, "❓")
    logger.info(f"{icon} [STATUS] Call {call_sid[:12]}... → {call_status} (duration: {duration}s)")

    return "", 204


if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", 5001))
    logger.info(f"🌐 Starting Interactive Webhook Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
