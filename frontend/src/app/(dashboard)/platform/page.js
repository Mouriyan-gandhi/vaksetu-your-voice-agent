"use client";
import React from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import Navbar from "@/components/Navbar";
const fadeUp = {
  initial: { opacity: 0, y: 30, filter: "blur(10px)" },
  whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
  transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
  viewport: { once: true }
};
import ScrollReveal from "@/components/ScrollReveal";
const ArchitectureItem = ({ step, title, desc, delay = 0 }) => (
  <ScrollReveal delay={delay} width="100%">
    <motion.div {...fadeUp} className="flex gap-8 group">
      <div className="w-12 h-12 rounded-full border border-border flex items-center justify-center font-mono text-xs flex-shrink-0 group-hover:border-saffron group-hover:text-saffron transition-all">
        {step}
      </div>
      <div>
        <h3 className="text-xl mb-2">{title}</h3>
        <p className="text-sm text-muted leading-relaxed">{desc}</p>
      </div>
    </motion.div>
  </ScrollReveal>
);
export default function PlatformPage() {
  return (
    <div className="relative pt-32 pb-40 px-6">
      <Navbar />
      <div className="noise-overlay" />
      <section className="max-w-7xl mx-auto space-y-32">
        {/* Header */}
        <ScrollReveal width="100%">
          <motion.div {...fadeUp} className="max-w-4xl">
            <span className="text-amber-glow font-mono text-xs uppercase tracking-widest mb-6 inline-block">Infrastructure Layer — Core API</span>
            <h1 className="text-fluid-h1 mb-8">Universal Voice <span className="italic font-display opacity-80">Intelligence</span></h1>
            <p className="text-xl text-muted leading-relaxed max-w-2xl">
              Just like Stripe provides payment infrastructure, VaakSetu provides voice intelligence infrastructure. One SDK. Infinite domains.
            </p>
          </motion.div>
        </ScrollReveal>
        {/* Dynamic API Preview */}
        <div className="grid lg:grid-cols-2 gap-6">
          <ScrollReveal width="100%" delay={0.2}>
            <div className="glass-card p-10 bg-ink-900 overflow-hidden font-mono text-xs leading-loose border-border/50 h-full">
              <div className="flex justify-between items-center mb-6">
                <span className="text-saffron uppercase">POST /api/v1/process</span>
                <span className="text-muted">healthcare-schema.json</span>
              </div>
              <pre className="text-cream-100/80">
                {`{
  "voice_stream": "blob_url_xyz",
  "domain": "healthcare",
  "config": {
    "dialect": "hinglish",
    "extract_entities": true,
    "escalate_on": ["panic", "fever_high"]
  }
}`}
              </pre>
            </div>
          </ScrollReveal>
          <ScrollReveal width="100%" delay={0.4}>
            <div className="glass-card p-10 bg-ink-900 border-border/50 font-mono text-xs leading-loose h-full">
              <div className="flex justify-between items-center mb-6 text-emerald-deep">
                <span className="uppercase">200 OK — AI Inference Complete</span>
                <span className="text-muted">214ms</span>
              </div>
              <pre className="text-emerald-deep/80">
                {`{
  "transcript": "Mujhe bukhar hai...",
  "entities": {
    "symptom": "fever",
    "risk_score": 0.85
  },
  "next_action": "clinical_escalation_needed"
}`}
              </pre>
            </div>
          </ScrollReveal>
        </div>
        {/* Architecture Flow */}
        <div className="grid md:grid-cols-2 gap-20">
          <div className="space-y-12">
            <ArchitectureItem step="01" title="Sovereign ASR" desc="Custom models trained on 10,000+ hours of Indic speech data. Handles accents, local slangs, and code-mixed grammar." delay={0.1} />
            <ArchitectureItem step="02" title="Contextual Reasoning" desc="LLM-based agent logic that maintains conversation context across 50+ turns. It doesn't just listen; it understands." delay={0.2} />
            <ArchitectureItem step="03" title="Structured JSON Extraction" desc="Turns messy human talk into reliable database fields. Plug this directly into your CRM or Hospital EHR." delay={0.3} />
            <ArchitectureItem step="04" title="RLAIF Reward Engine" desc="Self-evaluating safety and accuracy layer. Ensures medical and financial responses remain compliant." delay={0.4} />
          </div>
          <div className="flex items-center justify-center">
            <div className="w-full h-96 relative">
               <div className="absolute inset-0 bg-saffron/10 blur-[120px] rounded-full animate-pulse-slow" />
               <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-fluid-h2 font-display italic text-foreground/20 select-none text-center">
                    VAAKSETU <br/> INFRA
                  </div>
               </div>
            </div>
          </div>
        </div>
        {/* CTA */}
        <ScrollReveal width="100%">
          <div className="text-center py-20 border-t border-border/40">
            <p className="text-xs uppercase font-mono tracking-widest text-muted mb-8">Ready to Build for Bharat?</p>
            <Link href="/" className="text-fluid-h2 text-saffron underline hover:text-amber-glow transition-all">
                Request Sandbox Access →
            </Link>
          </div>
        </ScrollReveal>
      </section>
    </div>
  );
}
