"use client";
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { 
  ArrowLeft, CheckCircle2, XCircle, Clock, MessageSquare, 
  BarChart3, Shield, Smile, Languages, Scale, Loader2,
  FileJson, TrendingUp, Download
} from "lucide-react";
import Navbar from "@/components/Navbar";

const API_BASE = "/api";

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Stat Card
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function StatCard({ icon: Icon, label, value, color = "text-saffron", subtext = "" }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      className="bg-white/[0.03] border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
          <Icon size={18} className={color} />
        </div>
      </div>
      <p className="text-[10px] font-mono text-muted uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-2xl font-display ${color}`}>{value}</p>
      {subtext && <p className="text-[10px] font-mono text-muted mt-1">{subtext}</p>}
    </motion.div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Score Bar
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function ScoreBar({ label, score, max = 1, color = "bg-saffron" }) {
  const pct = Math.round((score / max) * 100);
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs">
        <span className="font-mono text-muted uppercase tracking-widest">{label}</span>
        <span className="font-mono text-white">{typeof score === "number" ? score.toFixed(2) : score}{max === 5 ? "/5" : ""}</span>
      </div>
      <div className="w-full bg-white/5 rounded-full h-2">
        <motion.div 
          className={`${color} rounded-full h-2`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}


export default function StatsPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const agentId = params.agentId;
  const sessionId = searchParams.get("sid");

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    if (sessionId) loadStats();
  }, [sessionId]);

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
      if (!res.ok) throw new Error("Failed to fetch session");
      const result = await res.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Navbar />
        <div className="text-center space-y-4">
          <Loader2 size={32} className="text-saffron animate-spin mx-auto" />
          <p className="text-muted text-sm">Loading session insights...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-32 px-6 max-w-2xl mx-auto text-center space-y-8">
          <XCircle size={48} className="text-red-400 mx-auto" />
          <h2 className="text-3xl font-display text-white">Error Loading Stats</h2>
          <p className="text-muted">{error || "Session data not found."}</p>
          <button onClick={() => router.push("/build")} className="btn-primary px-6 py-3 rounded-full text-sm">
            Back to Build
          </button>
        </div>
      </div>
    );
  }

  const { session, messages, agent, reward_scores } = data;
  const collected = session?.collected_fields || {};
  const scores = session?.reward_scores || reward_scores;
  const programmatic = scores?.programmatic;
  const llmJudge = scores?.llm_judge;
  const hasScores = programmatic && llmJudge;

  const totalMessages = messages?.length || 0;
  const userMessages = messages?.filter(m => m.role === "user").length || 0;
  const agentMessages = messages?.filter(m => m.role === "assistant").length || 0;

  const downloadSessionPdf = async () => {
    if (!data || !sessionId) return;
    setDownloadingPdf(true);
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 48;
      const contentWidth = pageWidth - margin * 2;
      let y = margin;

      const ensureSpace = (needed = 24) => {
        if (y + needed > pageHeight - margin) {
          doc.addPage();
          y = margin;
        }
      };

      const addTitle = (text) => {
        ensureSpace(36);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(20);
        doc.text(text, margin, y);
        y += 26;
      };

      const addSection = (title) => {
        ensureSpace(28);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(13);
        doc.text(title, margin, y);
        y += 16;
      };

      const addLine = (text, size = 10) => {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(size);
        const lines = doc.splitTextToSize(text, contentWidth);
        ensureSpace(lines.length * (size + 4) + 6);
        doc.text(lines, margin, y);
        y += lines.length * (size + 4) + 4;
      };

      addTitle("VaakSetu Session Report");
      addLine(`Generated: ${new Date().toISOString()}`);
      addLine(`Session ID: ${session.id}`);
      addLine(`Agent: ${agent?.name || "Unknown"} (${agent?.domain || "Unknown"})`);
      addLine(`Status: ${session?.status || "unknown"} | Complete: ${session?.is_complete ? "Yes" : "No"} | Turns: ${session?.turn_count || 0}`);
      addLine(`Messages: ${totalMessages} (User: ${userMessages}, Agent: ${agentMessages})`);

      addSection("Structured Fields");
      const collectedEntries = Object.entries(collected || {});
      if (collectedEntries.length === 0) {
        addLine("No structured fields collected.");
      } else {
        for (const [key, value] of collectedEntries) {
          addLine(`- ${key}: ${String(value)}`);
        }
      }

      addSection("Quality Scores");
      if (scores?.combined_reward != null) {
        addLine(`Combined Reward: ${scores.combined_reward}`);
        addLine(`DPO Label: ${scores.dpo_label || "n/a"}`);
      } else {
        addLine("No reward score available.");
      }
      if (programmatic) {
        addLine(`Programmatic - turn_efficiency=${programmatic.turn_efficiency}, sentiment_delta=${programmatic.sentiment_delta}, resolution_rate=${programmatic.resolution_rate}, content_safety=${programmatic.content_safety}`);
      }
      if (llmJudge) {
        addLine(`LLM Judge - politeness=${llmJudge.politeness}/5, accuracy=${llmJudge.accuracy}/5, indic_fluency=${llmJudge.indic_fluency}/5, policy_compliance=${llmJudge.policy_compliance}/5, resolution_quality=${llmJudge.resolution_quality}/5`);
        if (llmJudge.feedback) addLine(`Feedback: ${llmJudge.feedback}`);
      }

      addSection("Conversation Transcript");
      if (!messages?.length) {
        addLine("No transcript available.");
      } else {
        for (const msg of messages) {
          const roleLabel = msg.role === "user" ? "User" : (agent?.name || "Agent");
          addLine(`[Turn ${msg.turn_number}] ${roleLabel}: ${msg.content}`);
        }
      }

      doc.save(`vaaksetu_session_${sessionId}.pdf`);
    } catch (e) {
      setError(`PDF export failed: ${e.message}`);
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="noise-overlay" />

      <div className="pt-32 pb-40 px-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-12">
          <button onClick={() => router.push("/build")} className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition-all">
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-4xl font-display text-white">Session Insights</h1>
            <p className="text-muted font-mono text-xs uppercase tracking-widest mt-1">
              {agent?.name} — {session?.is_complete ? "Completed" : "Incomplete"} Session
            </p>
          </div>
          <div className="ml-auto">
            {session?.is_complete ? (
              <span className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-full text-emerald-500 text-xs font-mono uppercase tracking-widest">
                <CheckCircle2 size={14} /> All Fields Collected
              </span>
            ) : (
              <span className="flex items-center gap-2 bg-saffron/10 border border-saffron/20 px-4 py-2 rounded-full text-saffron text-xs font-mono uppercase tracking-widest">
                <XCircle size={14} /> Incomplete
              </span>
            )}
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <StatCard icon={MessageSquare} label="Total Messages" value={totalMessages} />
          <StatCard icon={Clock} label="Turns" value={session?.turn_count || 0} />
          <StatCard icon={FileJson} label="Fields Collected" value={`${Object.keys(collected).length}/${agent?.fields?.length || 0}`} color="text-emerald-500" />
          <StatCard 
            icon={TrendingUp} 
            label="Overall Score" 
            value={scores?.combined_reward ? `${(scores.combined_reward * 100).toFixed(0)}%` : "—"} 
            color={scores?.dpo_label === "chosen" ? "text-emerald-500" : "text-saffron"}
            subtext={scores?.dpo_label ? `DPO: ${scores.dpo_label}` : ""}
          />
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Extracted Data */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/[0.02] border border-white/10 rounded-3xl p-8">
            <h3 className="text-xl font-display text-white mb-6">Extracted Structured Data</h3>
            <div className="space-y-3">
              {Object.entries(collected).length > 0 ? (
                Object.entries(collected).map(([key, val]) => (
                  <div key={key} className="flex justify-between items-center py-3 border-b border-white/5">
                    <span className="text-[10px] font-mono text-muted uppercase tracking-widest">{key}</span>
                    <span className="text-sm text-white font-medium max-w-[60%] text-right">{String(val)}</span>
                  </div>
                ))
              ) : (
                <p className="text-muted text-sm italic text-center py-8">No fields were extracted.</p>
              )}
            </div>
          </motion.div>

          {/* RLAIF Scores */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white/[0.02] border border-white/10 rounded-3xl p-8">
            <h3 className="text-xl font-display text-white mb-6">RLAIF Quality Scores</h3>
            {hasScores ? (
              <div className="space-y-8">
                <div>
                  <p className="text-[10px] font-mono text-muted uppercase tracking-widest mb-4">Programmatic (40%)</p>
                  <div className="space-y-4">
                    <ScoreBar label="Turn Efficiency" score={programmatic.turn_efficiency} color="bg-cyan-vivid" />
                    <ScoreBar label="Sentiment Delta" score={programmatic.sentiment_delta} color="bg-emerald-500" />
                    <ScoreBar label="Resolution Rate" score={programmatic.resolution_rate} color="bg-saffron" />
                    <ScoreBar label="Content Safety" score={programmatic.content_safety} color="bg-green-500" />
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-mono text-muted uppercase tracking-widest mb-4">LLM Judge (60%)</p>
                  <div className="space-y-4">
                    <ScoreBar label="Politeness" score={llmJudge.politeness} max={5} color="bg-pink-500" />
                    <ScoreBar label="Accuracy" score={llmJudge.accuracy} max={5} color="bg-blue-500" />
                    <ScoreBar label="Indic Fluency" score={llmJudge.indic_fluency} max={5} color="bg-purple-500" />
                    <ScoreBar label="Policy Compliance" score={llmJudge.policy_compliance} max={5} color="bg-teal-500" />
                    <ScoreBar label="Resolution Quality" score={llmJudge.resolution_quality} max={5} color="bg-amber-500" />
                  </div>
                </div>
                {llmJudge.feedback && (
                  <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                    <p className="text-[10px] font-mono text-muted uppercase tracking-widest mb-2">LLM Feedback</p>
                    <p className="text-sm text-white italic">"{llmJudge.feedback}"</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 space-y-4">
                <BarChart3 size={32} className="text-muted mx-auto opacity-40" />
                <p className="text-muted text-sm">Scoring not available.</p>
                <p className="text-[10px] text-muted/60">Requires OPENAI_API_KEY for LLM judge scoring.</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Conversation Transcript */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mt-8 bg-white/[0.02] border border-white/10 rounded-3xl p-8">
          <h3 className="text-xl font-display text-white mb-6">Conversation Transcript</h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {messages?.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[70%] rounded-2xl px-5 py-3 ${
                  msg.role === "user" 
                    ? "bg-saffron/10 border border-saffron/20" 
                    : "bg-white/[0.03] border border-white/5"
                }`}>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                  <span className="text-[9px] font-mono text-muted mt-1 block">
                    {msg.role === "user" ? "User" : agent?.name || "Agent"} — Turn {msg.turn_number}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-6 mt-12">
          <button onClick={() => router.push("/build")} className="px-8 py-4 border border-white/10 rounded-full text-sm hover:bg-white/5 transition-all">
            Back to Agents
          </button>
          <button
            onClick={downloadSessionPdf}
            disabled={downloadingPdf}
            className="px-8 py-4 border border-saffron/30 text-saffron rounded-full text-sm hover:bg-saffron/10 transition-all disabled:opacity-50 flex items-center gap-2"
          >
            {downloadingPdf ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
            {downloadingPdf ? "Preparing PDF..." : "Download PDF"}
          </button>
          <button onClick={() => router.push(`/session/${agentId}`)} className="btn-primary px-8 py-4 rounded-full text-sm">
            Start New Session
          </button>
        </div>
      </div>
    </div>
  );
}
