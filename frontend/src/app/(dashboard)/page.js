"use client";
import React from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import DynamicLogo from "@/components/DynamicLogo";
import Navbar from "@/components/Navbar";
import MetricsBar from "@/components/MetricsBar";
import ScrollReveal from "@/components/ScrollReveal";
import FlowSequence from "@/components/FlowSequence";
import { 
  Activity, 
  Wallet, 
  GraduationCap, 
  Phone, 
  Settings, 
  Zap, 
  Database, 
  Cpu,
  ArrowRight
} from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 40, filter: "blur(10px)" },
  whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
  transition: { duration: 1, ease: [0.16, 1, 0.3, 1] },
  viewport: { once: true }
};

export default function HomePage() {
  return (
    <div className="relative overflow-x-hidden pt-20">
      <Navbar />
      <div className="noise-overlay" />

      {/* SECTION 1 — HERO */}
      <section className="h-[calc(100vh-80px)] flex flex-col justify-center items-center px-4 text-center space-y-4 overflow-hidden relative">
        <ScrollReveal width="100%">
          <div className="mb-4 transform scale-90 md:scale-100">
            <DynamicLogo />
          </div>
        </ScrollReveal>

        <ScrollReveal width="100%" delay={0.1}>
          <div className="max-w-6xl mx-auto space-y-3">
            <h1 className="text-2xl md:text-5xl lg:text-7xl leading-tight tracking-tighter font-display text-white whitespace-nowrap overflow-hidden text-ellipsis">
              Conversations → Intelligence → Action
            </h1>
            
            <p className="text-lg md:text-2xl text-saffron font-body font-medium tracking-wide max-w-3xl mx-auto opacity-80">
              Built for Bharat. Designed for multilingual reality.
            </p>
          </div>
        </ScrollReveal>

        <ScrollReveal width="100%" delay={0.2}>
          <div className="max-w-3xl mx-auto space-y-6">
            <p className="text-sm md:text-lg text-muted leading-relaxed font-body px-4 max-w-2xl mx-auto">
              “Millions of critical conversations are still lost in multilingual chaos — <br className="hidden md:block" />
              we turn them into structured, actionable intelligence.”
            </p>

            <div className="flex flex-row items-center justify-center gap-4">
              <Link href="/healthcare" className="btn-primary px-6 py-3 text-sm md:text-base group">
                Experience VaakSetu
                <motion.span 
                  className="inline-block ml-1 md:ml-2 group-hover:translate-x-1 transition-transform"
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  →
                </motion.span>
              </Link>
              <Link href="/platform" className="px-6 py-3 text-sm md:text-base font-medium border border-white/10 rounded-full hover:bg-white/5 transition-colors">
                View Platform API
              </Link>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* SECTION 2 — METRICS (The Proof) */}
      <section className="py-20 bg-zinc-950/20 border-y border-white/5">
        <div className="max-w-6xl mx-auto px-6">
           <MetricsBar />
        </div>
      </section>

      {/* SECTION 2 — CORE IDEA (Clarity) */}
      <section className="py-40 px-6 max-w-7xl mx-auto">
        <ScrollReveal width="100%">
            <h2 className="text-fluid-h2 mb-20 text-center">
              We don’t process speech. <br />
              <span className="italic font-display text-saffron">We transform it.</span>
            </h2>
        </ScrollReveal>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            { 
              title: "Understand", 
              desc: "Multilingual, code-mixed, real-world speech from any corner of India.", 
              icon: Cpu, 
              label: "Multi-Dialect Core" 
            },
            { 
              title: "Structure", 
              desc: "Convert chaotic conversations into clean, structured, and usable data schema.", 
              icon: Database, 
              label: "Intelligence Extraction" 
            },
            { 
              title: "Act", 
              desc: "Trigger real-world workflows, emergency decisions, and automated automation.", 
              icon: Zap, 
              label: "Action Engine" 
            }
          ].map((item, idx) => (
            <ScrollReveal key={idx} delay={idx * 0.2}>
              <div className="group relative bg-white/[0.02] border border-white/10 rounded-3xl p-10 h-full hover:border-saffron/40 transition-all duration-500 overflow-hidden">
                <div className="absolute -top-12 -right-12 text-9xl opacity-5 group-hover:opacity-10 transition-opacity rotate-12">
                   <item.icon size={120} />
                </div>
                <div className="text-saffron font-mono text-xs uppercase tracking-widest mb-6">{item.label}</div>
                <div className="text-4xl mb-4 text-saffron">
                   <item.icon size={40} />
                </div>
                <h3 className="text-3xl font-display mb-4 text-white">{item.title}</h3>
                <p className="text-lg text-muted leading-relaxed">{item.desc}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </section>

      {/* SECTION 3 — INTERACTIVE FLOW (Interactive/Wow) */}
      <section className="py-40 bg-zinc-950/30 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6">
          <ScrollReveal width="100%">
            <div className="text-center mb-24 space-y-6">
              <h2 className="text-fluid-h2">From Voice to Intelligence <br /> <span className="italic font-display opacity-80">— In Real Time</span></h2>
            </div>
          </ScrollReveal>
          
          <FlowSequence />
        </div>
      </section>

      {/* SECTION 4 — IMPACT (Scale) */}
      <section className="py-40 px-6 max-w-7xl mx-auto">
        <ScrollReveal width="100%">
          <div className="text-center mb-24">
            <h2 className="text-fluid-h2">One System. Every Industry. <br /> <span className="italic font-display text-saffron opacity-80">Infinite Scale.</span></h2>
          </div>
        </ScrollReveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { id: 'healthcare', title: "Healthcare", desc: "Triage & Emergency response with structured trauma records.", icon: Activity },
            { id: 'finance', title: "Finance", desc: "Multilingual loan verification and fraud intent detection.", icon: Wallet },
            { id: 'education', title: "Education", desc: "Structured learning progress and student intent mapping.", icon: GraduationCap },
            { id: 'sales', title: "Sales", desc: "Outbound automation that adapts to your user's dialect.", icon: Phone },
            { id: 'support', title: "Support", desc: "24/7 multilingual service that actually understands context.", icon: Settings }
          ].map((item, idx) => (
            <ScrollReveal key={idx} delay={idx * 0.1}>
              <Link href={item.id === 'finance' ? '/banking' : item.id === 'healthcare' ? '/healthcare' : '#'} 
                className="group p-8 border border-white/5 bg-white/[0.01] rounded-2xl hover:border-saffron/30 hover:bg-white/[0.03] transition-all flex items-center gap-6 shadow-2xl backdrop-blur-sm"
              >
                <div className="w-16 h-16 rounded-xl bg-white/5 flex items-center justify-center text-3xl group-hover:scale-110 transition-transform duration-500 shadow-inner">
                  <item.icon size={28} className="text-saffron/80" />
                </div>
                <div>
                  <h4 className="text-xl font-semibold text-white mb-1">{item.title}</h4>
                  <p className="text-sm text-muted leading-relaxed">{item.desc}</p>
                </div>
              </Link>
            </ScrollReveal>
          ))}
        </div>
      </section>

      {/* SECTION 5 — PHILOSOPHY (The Soul) */}
      <section className="py-64 px-6 text-center bg-saffron/[0.02]">
        <ScrollReveal width="100%">
          <div className="max-w-5xl mx-auto space-y-12">
            <h2 className="text-4xl md:text-7xl font-display leading-[1.1] text-white">
              “Multilingual is <span className="text-saffron italic">not a feature</span>. <br />
              It is the foundation.”
            </h2>
            <p className="text-2xl md:text-3xl text-muted font-body font-light tracking-wide max-w-3xl mx-auto opacity-80 py-8 border-y border-white/5">
              “We don’t make systems that adapt to language — <br />
              <span className="text-white italic">we build systems that are born in it.</span>”
            </p>
            <p className="text-xl text-saffron uppercase tracking-[0.3em] font-mono font-bold">— VaakSetu Built for Bharat —</p>
          </div>
        </ScrollReveal>
      </section>

      {/* SECTION 6 — PLATFORM PLAY */}
      <section className="py-40 px-6 max-w-7xl mx-auto">
        <div className="bg-gradient-to-br from-white/[0.03] to-transparent border border-white/10 rounded-[3rem] p-12 md:p-24 relative overflow-hidden text-center shadow-2xl backdrop-blur-3xl">
          <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-saffron/20 blur-[150px] rounded-full" />
          </div>
          
          <ScrollReveal width="100%">
            <div className="relative z-10 space-y-8">
              <h2 className="text-fluid-h2 tracking-tight">Built as <span className="italic font-display opacity-80">Infrastructure</span></h2>
              <p className="text-2xl text-muted max-w-2xl mx-auto font-body font-light">
                “Integrate VaakSetu into your system via APIs and unlock voice intelligence instantly.”
              </p>
              <div className="flex flex-col md:flex-row items-center justify-center gap-6 mt-12">
                <Link href="/platform" className="btn-primary px-12 py-5 text-xl font-semibold">Explore API</Link>
                <Link href="/platform" className="px-12 py-5 text-xl font-medium border border-white/10 rounded-full hover:bg-white/5 transition-all hover:scale-105 active:scale-95">
                  Start Integration
                </Link>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* SECTION 7 — FINAL CTA */}
      <section className="py-40 px-6 bg-zinc-950/80 border-t border-white/5">
        <ScrollReveal width="100%">
          <div className="max-w-4xl mx-auto text-center space-y-16">
            <h3 className="text-fluid-h3 font-display opacity-90 leading-tight">
              “If your users speak, <br />
              <span className="text-saffron italic">VaakSetu understands.</span>”
            </h3>
            <Link href="/healthcare" className="inline-block group relative">
                <div className="absolute -inset-4 bg-saffron/20 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <span className="relative btn-primary px-20 py-8 text-2xl font-bold rounded-full">
                    Build with VaakSetu
                </span>
            </Link>
            
            <div className="pt-24 border-t border-white/5 text-muted/40 font-mono text-xs flex flex-col md:flex-row justify-between items-center gap-6">
               <p>© 2026 VaakSetu. All Rights Reserved.</p>
               <div className="flex gap-12">
                 <a href="#" className="hover:text-saffron transition-colors underline-offset-4 hover:underline">Privacy</a>
                 <a href="#" className="hover:text-saffron transition-colors underline-offset-4 hover:underline">Terms</a>
                 <a href="#" className="hover:text-saffron transition-colors underline-offset-4 hover:underline">Documentation</a>
               </div>
            </div>
          </div>
        </ScrollReveal>
      </section>

    </div>
  );
}
