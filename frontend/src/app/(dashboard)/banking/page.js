"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Download, Loader2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import ScrollReveal from "@/components/ScrollReveal";
import { bankingUseCase } from "@/data/bankingUseCase";

const fadeUp = {
  initial: { opacity: 0, y: 30, filter: "blur(10px)" },
  whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
  transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  viewport: { once: true },
};

export default function BankingPage() {
  const [pdfLoading, setPdfLoading] = useState(false);

  const handleDownloadPdf = async () => {
    setPdfLoading(true);
    try {
      const { downloadBankingUseCasePdf } = await import("@/lib/useCaseDemoPdf");
      await downloadBankingUseCasePdf(bankingUseCase);
    } finally {
      setPdfLoading(false);
    }
  };

  const intentColor = (label) => {
    if (label === "Payment Status") return "text-saffron";
    if (label === "Confidence") return "text-emerald-deep";
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
              <span className="text-saffron font-mono text-xs uppercase tracking-widest mb-6 inline-block">
                {bankingUseCase.verticalLabel}
              </span>
              <h1 className="text-fluid-h1 mb-8">
                Loan & <span className="italic font-display opacity-80">Debt Automation</span>
              </h1>
              <p className="text-xl text-muted leading-relaxed max-w-2xl">{bankingUseCase.subtitle}</p>
            </div>
            <button
              type="button"
              onClick={handleDownloadPdf}
              disabled={pdfLoading}
              className="shrink-0 inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full border border-saffron/40 bg-saffron/10 text-saffron text-xs font-mono uppercase tracking-widest hover:bg-saffron/20 transition-all disabled:opacity-50 disabled:pointer-events-none"
            >
              {pdfLoading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
              {pdfLoading ? "Preparing PDF…" : "Download PDF summary"}
            </button>
          </motion.div>
        </ScrollReveal>
        {/* Call Flow Interface */}
        <ScrollReveal width="100%" delay={0.2}>
          <motion.div {...fadeUp} className="glass-card p-1 overflow-hidden bg-saffron/5 border-saffron/20">
            <div className="grid md:grid-cols-2 h-full">
              <div className="p-8 md:p-12 border-b md:border-b-0 md:border-r border-saffron/20 space-y-8 bg-background/20">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-2 h-2 rounded-full bg-saffron animate-ping" />
                  <span className="text-xs font-mono uppercase tracking-widest text-saffron">Outbound Call Sequence</span>
                </div>
                <div className="space-y-6">
                  {bankingUseCase.transcript.map((turn, i) =>
                    turn.role === "assistant" ? (
                      <div key={i} className="bg-saffron/10 p-5 rounded-2xl border border-saffron/30 max-w-[85%]">
                        <p className="text-sm font-medium">&ldquo;{turn.text}&rdquo;</p>
                        <p className="text-[10px] uppercase font-mono mt-2 text-saffron tracking-widest">{turn.meta}</p>
                      </div>
                    ) : (
                      <div key={i} className="bg-background/40 p-5 rounded-2xl border border-border/50 max-w-[85%] ml-auto text-right">
                        <p className="text-sm italic">&ldquo;{turn.text}&rdquo;</p>
                        <p className="text-[10px] uppercase font-mono mt-2 text-muted tracking-widest">{turn.meta}</p>
                      </div>
                    )
                  )}
                </div>
              </div>
              <div className="p-8 md:p-12 space-y-8 bg-background/30 backdrop-blur-3xl flex flex-col justify-between">
                <div>
                  <span className="text-xs font-mono uppercase tracking-widest text-muted">{bankingUseCase.structuredTitle}</span>
                  <div className="space-y-4 mt-8">
                    {bankingUseCase.structuredRows.map((item, i) => (
                      <div key={i} className="flex justify-between items-center py-3 border-b border-border/40">
                        <span className="text-[10px] uppercase font-mono tracking-widest text-muted">{item.label}</span>
                        <span className={`text-sm font-semibold tracking-tight ${intentColor(item.label)}`}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="pt-8 border-t border-border/10">
                  <button
                    type="button"
                    className="w-full py-4 rounded-xl border border-saffron text-saffron font-bold text-xs uppercase tracking-widest hover:bg-saffron hover:text-black transition-all"
                  >
                    Generate Compliance Audit Log
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </ScrollReveal>
        {/* Efficiency Section */}
        <div className="grid md:grid-cols-2 gap-20 items-center">
          <ScrollReveal>
            <div className="space-y-6">
              <h2 className="text-4xl text-foreground">
                Compliance-First <br /> Call Infrastructure
              </h2>
              <p className="text-muted text-sm leading-relaxed">{bankingUseCase.compliance.bullets[0]}</p>
              <p className="text-muted text-sm leading-relaxed">{bankingUseCase.compliance.bullets[1]}</p>
            </div>
          </ScrollReveal>
          <ScrollReveal delay={0.2}>
            <div className="glass-card p-10 bg-emerald-deep/5 border-emerald-deep/20 space-y-4 h-full">
              <div className="text-5xl font-display text-emerald-deep">84%</div>
              <p className="text-xs font-mono uppercase tracking-widest text-muted">Cost reduction vs Manual Call Centers</p>
            </div>
          </ScrollReveal>
        </div>
      </section>
    </div>
  );
}
