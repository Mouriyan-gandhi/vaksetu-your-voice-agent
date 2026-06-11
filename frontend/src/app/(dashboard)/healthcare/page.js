"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Download, Loader2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import ScrollReveal from "@/components/ScrollReveal";
import { healthcareUseCase } from "@/data/healthcareUseCase";

const fadeUp = {
  initial: { opacity: 0, y: 30, filter: "blur(10px)" },
  whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
  transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  viewport: { once: true },
};

export default function HealthcarePage() {
  const [pdfLoading, setPdfLoading] = useState(false);

  const handleDownloadPdf = async () => {
    setPdfLoading(true);
    try {
      const { downloadHealthcareUseCasePdf } = await import("@/lib/useCaseDemoPdf");
      await downloadHealthcareUseCasePdf(healthcareUseCase);
    } finally {
      setPdfLoading(false);
    }
  };

  const structuredColor = (label) => {
    if (label === "Risk Level") return "text-saffron";
    if (label === "Symptoms") return "text-cyan-vivid";
    return "text-foreground";
  };

  return (
    <div className="relative pt-32 pb-40 px-6">
      <Navbar />
      <div className="noise-overlay" />
      <section className="max-w-7xl mx-auto space-y-24">
        {/* Header */}
        <ScrollReveal width="100%">
          <motion.div {...fadeUp} className="max-w-4xl flex flex-col lg:flex-row lg:items-start lg:justify-between gap-8">
            <div className="space-y-6 flex-1">
              <span className="text-cyan-vivid font-mono text-xs uppercase tracking-widest mb-6 inline-block">
                {healthcareUseCase.verticalLabel}
              </span>
              <h1 className="text-fluid-h1 mb-8">
                Healthcare & <span className="italic font-display opacity-80">Emergency AI</span>
              </h1>
              <p className="text-xl text-muted leading-relaxed max-w-2xl">{healthcareUseCase.subtitle}</p>
            </div>
            <button
              type="button"
              onClick={handleDownloadPdf}
              disabled={pdfLoading}
              className="shrink-0 inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full border border-cyan-vivid/40 bg-cyan-vivid/10 text-cyan-vivid text-xs font-mono uppercase tracking-widest hover:bg-cyan-vivid/20 transition-all disabled:opacity-50 disabled:pointer-events-none"
            >
              {pdfLoading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
              {pdfLoading ? "Preparing PDF…" : "Download PDF summary"}
            </button>
          </motion.div>
        </ScrollReveal>
        {/* Live Simulation Card */}
        <ScrollReveal width="100%" delay={0.2}>
          <motion.div
            {...fadeUp}
            className="glass-card p-1 md:p-1 overflow-hidden bg-cyan-vivid/5 border-cyan-vivid/20"
          >
            <div className="grid md:grid-cols-2">
              <div className="p-8 md:p-12 border-b md:border-b-0 md:border-r border-cyan-vivid/20 space-y-8">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-2 h-2 rounded-full bg-cyan-vivid animate-pulse" />
                  <span className="text-xs font-mono uppercase tracking-widest text-cyan-vivid">Voice Stream Active</span>
                </div>
                <div className="space-y-6">
                  {healthcareUseCase.transcript.map((turn, i) =>
                    turn.role === "patient" ? (
                      <div key={i} className="bg-background/40 p-5 rounded-2xl border border-border/50 max-w-[80%]">
                        <p className="text-sm italic">&ldquo;{turn.text}&rdquo;</p>
                        <p className="text-[10px] uppercase font-mono mt-2 text-muted tracking-widest">{turn.meta}</p>
                      </div>
                    ) : (
                      <div
                        key={i}
                        className="bg-cyan-vivid/10 p-5 rounded-2xl border border-cyan-vivid/30 max-w-[80%] ml-auto text-right"
                      >
                        <p className="text-sm font-medium">&ldquo;{turn.text}&rdquo;</p>
                        <p className="text-[10px] uppercase font-mono mt-2 text-cyan-vivid tracking-widest">{turn.meta}</p>
                      </div>
                    )
                  )}
                </div>
                <div className="pt-8 border-t border-cyan-vivid/10">
                  <div className="flex items-center justify-between">
                    <div className="flex space-x-2">
                      {[1, 2, 3].map((i) => (
                        <div
                          key={i}
                          className="w-1.5 h-1.5 rounded-full bg-cyan-vivid/40 h-8 md:h-12 w-1 animate-pulse"
                          style={{ animationDelay: `${i * 0.2}s` }}
                        />
                      ))}
                    </div>
                    <button type="button" className="px-6 py-2 rounded-full border border-cyan-vivid/40 bg-cyan-vivid/10 text-xs font-mono uppercase tracking-widest text-cyan-vivid">
                      Stop Session
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-8 md:p-12 space-y-8 bg-background/30 backdrop-blur-3xl">
                <span className="text-xs font-mono uppercase tracking-widest text-muted">{healthcareUseCase.structuredTitle}</span>
                <div className="space-y-4">
                  {healthcareUseCase.structuredRows.map((item, i) => (
                    <div key={i} className="flex justify-between items-center py-3 border-b border-border/40">
                      <span className="text-[10px] uppercase font-mono tracking-widest text-muted">{item.label}</span>
                      <span className={`text-sm font-semibold tracking-tight ${structuredColor(item.label)}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
                <div className="p-5 rounded-2xl border border-saffron/20 bg-saffron/5">
                  <p className="text-[10px] uppercase font-mono mb-2 text-saffron tracking-widest">{healthcareUseCase.highlight.title}</p>
                  <p className="text-xs text-muted leading-relaxed">{healthcareUseCase.highlight.body}</p>
                </div>
              </div>
            </div>
          </motion.div>
        </ScrollReveal>
        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {healthcareUseCase.features.map((feature, i) => (
            <ScrollReveal key={feature.title} delay={i * 0.1}>
              <motion.div {...fadeUp} transition={{ delay: i * 0.2 }} className="glass-card p-10 border border-border/50 h-full">
                <h3 className="text-2xl mb-4 font-display">{feature.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{feature.desc}</p>
              </motion.div>
            </ScrollReveal>
          ))}
        </div>
      </section>
    </div>
  );
}
