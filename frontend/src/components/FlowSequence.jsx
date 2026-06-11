"use client";
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Target, Settings, Cpu, Zap } from "lucide-react";

const STEPS = [
  {
    id: 1,
    title: "Input",
    subtitle: "Multimodal Capture",
    content: "Voice | Image | Text",
    description: "Capturing human intent in any form, across any dialect.",
    icon: Mic
  },
  {
    id: 2,
    title: "Select Domain",
    subtitle: "Contextual Awareness",
    content: "Healthcare | Finance | Education | Custom",
    description: "Applying industry-specific logic and vocabulary constraints.",
    icon: Target
  },
  {
    id: 3,
    title: "Configure Agent",
    subtitle: "Behavioral Mapping",
    content: "Name: 'Triage-Helper' | Fields: 'Symptoms, Risk' | Escalation: 'Emergency'",
    description: "Defining triggers, required data fields, and workflow paths.",
    icon: Settings
  },
  {
    id: 4,
    title: "AI Core",
    subtitle: "Intelligence Layer",
    content: "Optimized System Prompts + Multilingual RLAIF",
    description: "High-precision extraction through sovereign multilingual intelligence.",
    icon: Cpu
  },
  {
    id: 5,
    title: "Output",
    subtitle: "Actionable Results",
    content: "Structured Data | AI Response | Workflow Triggered",
    description: "The conversation is now data. The action is now automated.",
    icon: Zap
  }
];

export default function FlowSequence() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % STEPS.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full max-w-5xl mx-auto py-20 px-4">
      <div className="relative">
        {/* Progress Bar Container */}
        <div className="absolute top-1/2 left-0 w-full h-[2px] bg-white/5 -translate-y-1/2 hidden md:block" />
        
        {/* Progress Fill */}
        <motion.div 
          className="absolute top-1/2 left-0 h-[2px] bg-saffron -translate-y-1/2 hidden md:block shadow-[0_0_15px_rgba(249,115,22,0.5)]"
          initial={{ width: "0%" }}
          animate={{ width: `${(activeStep / (STEPS.length - 1)) * 100}%` }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        />

        <div className="relative flex flex-col md:flex-row justify-between items-start md:items-center gap-12 md:gap-4">
          {STEPS.map((step, index) => {
            const isActive = index === activeStep;
            const isCompleted = index < activeStep;

            return (
              <div 
                key={step.id}
                className="relative z-10 flex flex-col items-center group cursor-pointer"
                onClick={() => setActiveStep(index)}
              >
                {/* Connector Dot */}
                <motion.div 
                  className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-500 bg-background
                    ${isActive ? 'border-saffron scale-110 shadow-[0_0_20px_rgba(249,115,22,0.3)]' : 
                      isCompleted ? 'border-saffron bg-saffron/10' : 'border-white/10'}`}
                >
                  <step.icon 
                    size={20}
                    className={`${isActive || isCompleted ? 'text-saffron opacity-100' : 'text-muted opacity-30'}`}
                  />
                </motion.div>

                {/* Step Label (Desktop) */}
                <div className="absolute top-16 text-center w-32 hidden md:block">
                  <p className={`text-xs font-mono uppercase tracking-widest transition-colors duration-500
                    ${isActive ? 'text-saffron' : 'text-muted'}`}>
                    Step {step.id}
                  </p>
                  <p className={`text-sm font-semibold mt-1 transition-colors duration-500
                     ${isActive ? 'text-white' : 'text-muted'}`}>
                    {step.title}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Display Card */}
      <div className="mt-40">
        <AnimatePresence mode="wait">
          <motion.div 
            key={activeStep}
            initial={{ opacity: 0, y: 20, filter: "blur(10px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: -20, filter: "blur(10px)" }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="grid md:grid-cols-2 gap-12 items-center bg-white/[0.02] border border-white/5 rounded-3xl p-8 md:p-16 backdrop-blur-3xl"
          >
            <div>
              <span className="text-saffron font-mono text-xs uppercase tracking-widest mb-4 inline-block">
                Process Stage {STEPS[activeStep].id}
              </span>
              <h3 className="text-4xl md:text-5xl font-display mb-4 text-white">
                {STEPS[activeStep].title}
              </h3>
              <p className="text-xl text-saffron/80 font-medium mb-6 italic opacity-80">
                {STEPS[activeStep].subtitle}
              </p>
              <p className="text-lg text-muted leading-relaxed mb-8">
                {STEPS[activeStep].description}
              </p>
            </div>

            <div className="relative group">
              <div className="absolute -inset-4 bg-saffron/10 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
              <div className="relative bg-white/[0.03] border border-white/10 rounded-2xl p-8 font-mono text-xl md:text-2xl text-center shadow-2xl overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-saffron/30 to-transparent" />
                <span className="text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
                  {STEPS[activeStep].content}
                </span>
                <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-saffron/30 to-transparent" />
                
                {/* Animated Scan Line */}
                <motion.div 
                    initial={{ top: "-100%" }}
                    animate={{ top: "200%" }}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    className="absolute left-0 w-full h-1/2 bg-gradient-to-b from-transparent via-saffron/5 to-transparent pointer-events-none"
                />
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
