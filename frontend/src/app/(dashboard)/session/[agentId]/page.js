"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import {
  Send, Mic, Square, Loader2, CheckCircle2,
  ArrowLeft, AlertTriangle, Volume2, VolumeX
} from "lucide-react";
import Navbar from "@/components/Navbar";

const API_BASE   = "/api";
const API_DIRECT = typeof window !== "undefined"
  ? `http://${window.location.hostname}:8000/api`
  : "http://localhost:8000/api";

// ─────────────────────────────────────────────────────────────────────────────
// TTS Engine
// Priority 1: Sarvam base64 WAV from backend (high-quality, Indian languages)
// Priority 2: browser SpeechSynthesis (zero-config fallback, always works)
// ─────────────────────────────────────────────────────────────────────────────
class TTSEngine {
  constructor() {
    this._unlocked  = false;   // becomes true after first user gesture
    this._queue     = [];      // [{b64, text, lang}]
    this._playing   = false;
    this._muted     = false;
    this._audioEl   = null;
    this._onState   = null;    // callback(isPlaying)
  }

  /** Call after any user click to unlock browser autoplay */
  unlock() {
    if (this._unlocked) return;
    this._unlocked = true;
    this._flush();
  }

  setMuted(v) {
    this._muted = v;
    if (v) this.stop();
  }

  /** Enqueue an utterance. b64 may be null → will use SpeechSynthesis */
  enqueue(b64, text, lang = "hi-IN") {
    this._queue.push({ b64, text, lang });
    this._flush();
  }

  stop() {
    this._queue = [];
    this._playing = false;
    if (this._audioEl) { this._audioEl.pause(); this._audioEl = null; }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    this._notify(false);
  }

  _notify(v) {
    if (this._onState) this._onState(v);
  }

  _flush() {
    if (this._muted || this._playing || !this._unlocked) return;
    if (!this._queue.length) return;
    const item = this._queue.shift();
    this._playing = true;
    this._notify(true);

    if (item.b64) {
      this._playB64(item.b64, item.text, item.lang);
    } else {
      this._playSpeechSynthesis(item.text, item.lang);
    }
  }

  _playB64(b64, text, lang) {
    try {
      const audio = new Audio(`data:audio/wav;base64,${b64}`);
      this._audioEl = audio;
      audio.onended = () => { this._playing = false; this._notify(false); this._flush(); };
      audio.onerror = () => {
        console.warn("WAV playback failed, falling back to SpeechSynthesis");
        this._playing = false;
        this._audioEl = null;
        this._playSpeechSynthesis(text, lang);
      };
      audio.play().catch(() => {
        // Autoplay still blocked despite unlock attempt
        this._playing = false;
        this._notify(false);
        this._playSpeechSynthesis(text, lang);
      });
    } catch (e) {
      this._playing = false;
      this._playSpeechSynthesis(text, lang);
    }
  }

  _playSpeechSynthesis(text, lang) {
    if (!text || !window.speechSynthesis) {
      this._playing = false;
      this._notify(false);
      this._flush();
      return;
    }

    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);

    // Map Sarvam lang codes → browser lang codes
    const langMap = {
      "hi-IN": "hi-IN", "en-IN": "en-IN", "bn-IN": "bn-IN",
      "ta-IN": "ta-IN", "te-IN": "te-IN", "kn-IN": "kn-IN",
      "ml-IN": "ml-IN", "mr-IN": "mr-IN", "gu-IN": "gu-IN",
      "pa-IN": "pa-IN", "od-IN": "or-IN",
    };
    utt.lang = langMap[lang] || "hi-IN";
    utt.rate = 0.95;
    utt.pitch = 1.0;
    utt.volume = 1.0;

    // Pick an Indian voice if available
    const voices = window.speechSynthesis.getVoices();
    const indVoice = voices.find(v =>
      v.lang.startsWith(utt.lang) ||
      v.lang.startsWith("hi") ||
      v.name.toLowerCase().includes("india")
    );
    if (indVoice) utt.voice = indVoice;

    utt.onend  = () => { this._playing = false; this._notify(false); this._flush(); };
    utt.onerror = () => { this._playing = false; this._notify(false); this._flush(); };

    window.speechSynthesis.speak(utt);
  }
}

// Singleton shared across renders
const _ttsEngine = typeof window !== "undefined" ? new TTSEngine() : null;

function useTTS() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted,   setIsMuted  ] = useState(false);

  useEffect(() => {
    if (!_ttsEngine) return;
    _ttsEngine._onState = setIsPlaying;
    return () => { _ttsEngine._onState = null; };
  }, []);

  const enqueue = useCallback((b64, text, lang) => {
    _ttsEngine?.enqueue(b64, text, lang);
  }, []);

  const stop = useCallback(() => { _ttsEngine?.stop(); }, []);

  const unlock = useCallback(() => { _ttsEngine?.unlock(); }, []);

  const toggleMute = useCallback(() => {
    setIsMuted(prev => {
      const next = !prev;
      _ttsEngine?.setMuted(next);
      return next;
    });
  }, []);

  return { enqueue, stop, unlock, toggleMute, isPlaying, isMuted };
}

// ─────────────────────────────────────────────────────────────────────────────
// Speaking animation
// ─────────────────────────────────────────────────────────────────────────────
function SpeakingBars() {
  return (
    <span className="inline-flex items-end gap-[2px] ml-1.5 mb-0.5">
      {[0.3, 0.6, 1, 0.7, 0.4].map((h, i) => (
        <span
          key={i}
          style={{
            display: "inline-block",
            width: 3,
            borderRadius: 2,
            background: "#f97316",
            animation: `speakBar 0.7s ease-in-out ${i * 0.1}s infinite alternate`,
            height: `${h * 14}px`,
          }}
        />
      ))}
      <style>{`
        @keyframes speakBar {
          from { transform: scaleY(0.3); opacity:0.5; }
          to   { transform: scaleY(1);   opacity:1; }
        }
      `}</style>
    </span>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Session Page
// ─────────────────────────────────────────────────────────────────────────────
export default function SessionPage() {
  const params  = useParams();
  const router  = useRouter();
  const agentId = params.agentId;

  const [agent,           setAgent          ] = useState(null);
  const [sessionId,       setSessionId      ] = useState(null);
  const [messages,        setMessages       ] = useState([]);
  const [input,           setInput          ] = useState("");
  const [sending,         setSending        ] = useState(false);
  const [collectedFields, setCollectedFields] = useState({});
  const [missingFields,   setMissingFields  ] = useState([]);
  const [isComplete,      setIsComplete     ] = useState(false);
  const [isRecording,     setIsRecording    ] = useState(false);
  const [error,           setError          ] = useState(null);
  const [ending,          setEnding         ] = useState(false);
  const [audioUnlocked,   setAudioUnlocked  ] = useState(false);

  // Pending greeting audio waiting for user click
  const pendingGreeting = useRef(null);

  const messagesEndRef   = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef   = useRef([]);

  const tts = useTTS();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (agentId) startSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  // ── Unlock audio on first page interaction ─────────────────────
  const unlockAndPlay = useCallback(() => {
    if (audioUnlocked) return;
    tts.unlock();
    setAudioUnlocked(true);
    // Play any greeting that was queued before unlock
    if (pendingGreeting.current) {
      const { b64, text, lang } = pendingGreeting.current;
      tts.enqueue(b64, text, lang);
      pendingGreeting.current = null;
    }
  }, [audioUnlocked, tts]);

  // ── Session Start ───────────────────────────────────────────────
  const startSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId }),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || "Failed to start session");
      }
      const data = await res.json();
      setAgent(data.agent);
      setSessionId(data.session_id);
      setMissingFields(data.missing_fields || []);

      const lang = data.language_code || data.agent?.default_language || "hi-IN";
      const msg  = { role: "assistant", content: data.greeting, audio: data.greeting_audio, lang };
      setMessages([msg]);

      // Store greeting - will play on first user interaction to bypass autoplay block
      pendingGreeting.current = {
        b64:  data.greeting_audio,
        text: data.greeting,
        lang,
      };
    } catch (err) {
      setError(`Failed to start session: ${err.message}. Make sure the backend is running on port 8000.`);
    }
  };

  // ── Send Message ────────────────────────────────────────────────
  const sendMessage = async (text, languageCode = null) => {
    if (!text.trim() || !sessionId || sending) return;
    unlockAndPlay();     // ensure audio is unlocked on send
    tts.stop();          // stop agent speaking when user sends

    setMessages(prev => [...prev, { role: "user", content: text.trim() }]);
    setInput("");
    setSending(true);

    try {
      const res = await fetch(`${API_DIRECT}/sessions/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text.trim(), input_type: "text", language_code: languageCode }),
      });
      if (!res.ok) throw new Error("Send failed");
      const data = await res.json();

      const lang    = data.language_code || agent?.default_language || "hi-IN";
      const asstMsg = { role: "assistant", content: data.response, audio: data.response_audio, lang };
      setMessages(prev => [...prev, asstMsg]);
      setCollectedFields(data.collected_fields || {});
      setMissingFields(data.missing_fields || []);
      setIsComplete(data.is_complete || false);

      // Play response — Sarvam WAV if available, else SpeechSynthesis
      tts.enqueue(data.response_audio || null, data.response, lang);

      if (data.is_escalation) {
        setMessages(prev => [...prev, {
          role: "system",
          content: "⚠️ Escalation triggered — connecting to human agent.",
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "system",
        content: "Failed to get response. Please try again.",
      }]);
    } finally {
      setSending(false);
    }
  };

  // ── Voice Recording ─────────────────────────────────────────────
  const startRecording = async () => {
    try {
      unlockAndPlay();
      tts.stop();
      const stream   = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus" : "audio/webm";
      const rec = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = rec;
      audioChunksRef.current   = [];
      rec.ondataavailable = e => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        await transcribeAndSend(blob);
      };
      rec.start();
      setIsRecording(true);
    } catch {
      setError("Microphone access denied. Please allow mic access in browser settings.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAndSend = async (blob) => {
    setSending(true);
    try {
      const fd = new FormData();
      fd.append("audio", blob, "recording.webm");
      const res  = await fetch(`${API_DIRECT}/transcribe`, { method: "POST", body: fd });
      if (!res.ok) throw new Error("Transcription failed");
      const data = await res.json();
      if (data.transcript) {
        await sendMessage(data.transcript, data.language_code);
      } else {
        setError("Could not transcribe. Please type instead.");
        setSending(false);
      }
    } catch {
      setError("Voice transcription failed. Please type instead.");
      setSending(false);
    }
  };

  // ── Replay a message ────────────────────────────────────────────
  const replayMessage = (msg) => {
    tts.stop();
    tts.enqueue(msg.audio || null, msg.content, msg.lang || "hi-IN");
  };

  // ── End Session ─────────────────────────────────────────────────
  const endSession = async () => {
    if (!sessionId) return;
    tts.stop();
    setEnding(true);
    try {
      await fetch(`${API_BASE}/sessions/${sessionId}/end`, { method: "POST" });
      router.push(`/session/${agentId}/stats?sid=${sessionId}`);
    } catch {
      setError("Failed to end session.");
      setEnding(false);
    }
  };

  // ── Computed ────────────────────────────────────────────────────
  const voiceEnabled  = agent?.inputs?.includes("Voice");
  const fieldProgress = agent?.fields?.length
    ? Math.round((Object.keys(collectedFields).length / agent.fields.length) * 100)
    : 0;

  if (error && !sessionId) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-32 px-6 max-w-2xl mx-auto text-center space-y-8">
          <AlertTriangle size={48} className="text-saffron mx-auto" />
          <h2 className="text-3xl font-display text-white">Connection Error</h2>
          <p className="text-muted leading-relaxed">{error}</p>
          <div className="flex gap-4 justify-center">
            <button onClick={() => router.push("/build")} className="px-6 py-3 border border-white/10 rounded-full text-sm hover:bg-white/5 transition-all">Back to Build</button>
            <button onClick={() => { setError(null); startSession(); }} className="btn-primary px-6 py-3 rounded-full text-sm">Retry</button>
          </div>
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Navbar />
        <Loader2 size={32} className="text-saffron animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col" onClick={unlockAndPlay}>
      <Navbar />
      <div className="noise-overlay" />

      <div className="flex-1 flex pt-20">
        {/* ── Chat Area ── */}
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4">

          {/* Header */}
          <div className="py-6 flex items-center justify-between border-b border-white/5">
            <div className="flex items-center gap-4">
              <button onClick={() => router.push("/build")} className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition-all">
                <ArrowLeft size={18} />
              </button>
              <div>
                <div className="flex items-center gap-1">
                  <h2 className="text-xl font-display text-white">{agent.name}</h2>
                  {tts.isPlaying && !tts.isMuted && <SpeakingBars />}
                </div>
                <span className="text-[10px] font-mono text-saffron uppercase tracking-widest">
                  {agent.domain === "Others" ? agent.customDomain : agent.domain}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {isComplete && (
                <span className="flex items-center gap-2 text-emerald-500 text-xs font-mono uppercase tracking-widest">
                  <CheckCircle2 size={14} /> Complete
                </span>
              )}

              {/* Mute toggle */}
              <button
                onClick={(e) => { e.stopPropagation(); unlockAndPlay(); tts.toggleMute(); }}
                title={tts.isMuted ? "Unmute agent voice" : "Mute agent voice"}
                className={`w-9 h-9 rounded-full flex items-center justify-center border transition-all ${
                  tts.isMuted
                    ? "bg-white/5 border-white/10 text-muted hover:text-white"
                    : "bg-saffron/10 border-saffron/30 text-saffron hover:bg-saffron/20"
                }`}
              >
                {tts.isMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
              </button>

              <button
                onClick={endSession}
                disabled={ending}
                className="px-5 py-2 rounded-full border border-saffron/40 text-saffron text-xs font-mono uppercase tracking-widest hover:bg-saffron/10 transition-all disabled:opacity-50"
              >
                {ending ? "Ending..." : "End Session"}
              </button>
            </div>
          </div>

          {/* ── Audio unlock prompt (only shown before first interaction) ── */}
          {!audioUnlocked && messages.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-3 flex items-center gap-3 px-4 py-2.5 bg-saffron/8 border border-saffron/20 rounded-xl cursor-pointer hover:bg-saffron/12 transition-all"
              onClick={(e) => { e.stopPropagation(); unlockAndPlay(); }}
            >
              <Volume2 size={15} className="text-saffron flex-shrink-0" />
              <span className="text-xs text-saffron/80 font-mono">
                Click here to enable voice — agent will speak its responses aloud
              </span>
            </motion.div>
          )}

          {/* ── Messages ── */}
          <div className="flex-1 overflow-y-auto py-8 space-y-6">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "system" ? (
                  <div className="bg-saffron/10 border border-saffron/20 rounded-2xl px-5 py-3 max-w-lg">
                    <p className="text-sm text-saffron">{msg.content}</p>
                  </div>
                ) : (
                  <div className={`max-w-[75%] rounded-3xl px-6 py-4 group relative ${
                    msg.role === "user"
                      ? "bg-saffron/15 border border-saffron/20 text-white"
                      : "bg-white/[0.04] border border-white/10 text-white"
                  }`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    <div className={`flex items-center mt-2 gap-2 ${msg.role === "user" ? "justify-end" : "justify-between"}`}>
                      <span className={`text-[9px] font-mono uppercase tracking-widest ${
                        msg.role === "user" ? "text-saffron/60" : "text-muted"
                      }`}>
                        {msg.role === "user" ? "You" : agent.name}
                      </span>
                      {/* Replay button on agent messages */}
                      {msg.role === "assistant" && (
                        <button
                          onClick={(e) => { e.stopPropagation(); unlockAndPlay(); replayMessage(msg); }}
                          title="Replay"
                          className="opacity-0 group-hover:opacity-100 transition-opacity text-muted hover:text-saffron"
                        >
                          <Volume2 size={12} />
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}

            {sending && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="bg-white/[0.04] border border-white/10 rounded-3xl px-6 py-4 flex items-center gap-3">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 rounded-full bg-saffron/50 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                  <span className="text-[10px] font-mono text-muted">Thinking...</span>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* ── Input Area ── */}
          <div className="pb-6 pt-4 border-t border-white/5">
            {error && (
              <div className="mb-3 bg-saffron/10 border border-saffron/20 rounded-xl px-4 py-2 flex items-center justify-between">
                <p className="text-xs text-saffron">{error}</p>
                <button onClick={() => setError(null)} className="text-saffron hover:text-white ml-3">✕</button>
              </div>
            )}

            <div className="flex items-center gap-3">
              {voiceEnabled && (
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={sending}
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all border ${
                    isRecording
                      ? "bg-red-500/20 border-red-500 text-red-400 animate-pulse"
                      : "bg-white/5 border-white/10 text-muted hover:text-saffron hover:border-saffron/30"
                  } disabled:opacity-50`}
                >
                  {isRecording ? <Square size={18} /> : <Mic size={18} />}
                </button>
              )}
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); } }}
                placeholder={isRecording ? "Recording… click ■ to send" : "Type or use mic…"}
                disabled={sending || isRecording}
                className="flex-1 bg-white/[0.03] border border-white/10 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:border-saffron/40 transition-all disabled:opacity-50 placeholder:text-muted/50"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || sending}
                className="w-12 h-12 rounded-full bg-saffron flex items-center justify-center text-black hover:scale-105 active:scale-95 transition-all disabled:opacity-30"
              >
                <Send size={18} />
              </button>
            </div>

            {tts.isPlaying && !tts.isMuted && (
              <p className="mt-2 text-[10px] font-mono text-saffron/60 flex items-center gap-1.5">
                <Volume2 size={10} />
                Agent speaking…
                <button onClick={(e) => { e.stopPropagation(); tts.stop(); }} className="underline hover:text-saffron ml-1">
                  Skip
                </button>
              </p>
            )}
          </div>
        </div>

        {/* ── Right Sidebar ── */}
        <div className="hidden lg:block w-72 border-l border-white/5 p-6 overflow-y-auto">
          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest mb-4">Progress</h3>
              <div className="w-full bg-white/5 rounded-full h-2 mb-2">
                <motion.div
                  className="bg-saffron rounded-full h-2"
                  initial={{ width: 0 }}
                  animate={{ width: `${fieldProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <span className="text-[10px] font-mono text-muted">{fieldProgress}% complete</span>
            </div>

            {/* Voice Status */}
            <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-4 space-y-3">
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest">Voice</h3>
              <div className="space-y-2 text-[10px] font-mono">
                <div className="flex justify-between">
                  <span className="text-muted">Status</span>
                  <span className={
                    tts.isMuted ? "text-red-400" :
                    tts.isPlaying ? "text-saffron" : "text-emerald-400"
                  }>
                    {tts.isMuted ? "Muted" : tts.isPlaying ? "▶ Speaking" : "Ready"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Language</span>
                  <span className="text-saffron">{agent.default_language || "hi-IN"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Engine</span>
                  <span className="text-muted">Sarvam Bulbul v2</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Unlocked</span>
                  <span className={audioUnlocked ? "text-emerald-400" : "text-red-400"}>
                    {audioUnlocked ? "Yes" : "No — click to enable"}
                  </span>
                </div>
              </div>
            </div>

            {/* Collected */}
            <div>
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest mb-3">Collected</h3>
              <div className="space-y-2">
                {Object.entries(collectedFields).map(([k, v]) => (
                  <div key={k} className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3">
                    <span className="text-[10px] font-mono text-emerald-500 uppercase tracking-widest block">{k}</span>
                    <span className="text-xs text-white mt-1 block">{String(v)}</span>
                  </div>
                ))}
                {!Object.keys(collectedFields).length && (
                  <p className="text-[10px] font-mono text-muted italic">No fields yet</p>
                )}
              </div>
            </div>

            {/* Pending */}
            <div>
              <h3 className="text-xs font-mono text-muted uppercase tracking-widest mb-3">Pending</h3>
              <div className="space-y-1.5">
                {missingFields.map(f => (
                  <div key={f} className="bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2">
                    <span className="text-[10px] font-mono text-muted">{f}</span>
                  </div>
                ))}
                {!missingFields.length && (
                  <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3 text-center">
                    <CheckCircle2 size={18} className="text-emerald-500 mx-auto mb-1" />
                    <span className="text-[10px] font-mono text-emerald-500">All collected!</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
