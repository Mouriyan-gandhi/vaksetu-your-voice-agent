"use client";
import React, { useEffect, useState, useRef } from "react";
import { motion, useInView } from "framer-motion";

function AnimatedCounter({ target, suffix = "", prefix = "" }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (isInView) {
      let start = 0;
      const end = parseInt(target);
      if (start === end) {
        setCount(end);
        return;
      }

      let totalMiliseconds = 2000;
      let incrementTime = (totalMiliseconds / end) > 10 ? (totalMiliseconds / end) : 10;
      let timer = setInterval(() => {
        start += 1;
        setCount(start);
        if (start === end) clearInterval(timer);
      }, incrementTime);
      return () => clearInterval(timer);
    }
  }, [isInView, target]);

  return (
    <span ref={ref} className="tabular-nums">
      {prefix}{count}{suffix}
    </span>
  );
}

export default function MetricsBar() {
  const metrics = [
    { label: "ASR LANGUAGES", value: 11, suffix: "+", prefix: "", detail: "INDIC DIALECTS SUPPORTED" },
    { label: "VOICE LATENCY", value: 450, suffix: "ms", prefix: "<", detail: "REAL-TIME INFERENCE" },
    { label: "UPTIME", value: 99, suffix: "%", prefix: "", detail: "SOVEREIGN COMPUTE CLOUD" },
    { label: "PERSONA MODELS", value: 48, suffix: "", prefix: "", detail: "CUSTOM FINE-TUNED AGENTS" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-12 w-full">
      {metrics.map((m, i) => (
        <div key={i} className="flex flex-col space-y-2">
          <div className="text-4xl md:text-5xl font-display text-foreground flex items-baseline gap-1">
            <AnimatedCounter target={m.value} suffix={m.suffix} prefix={m.prefix} />
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-mono uppercase tracking-widest text-foreground font-semibold">
              {m.label}
            </p>
            <p className="text-[10px] font-mono text-muted uppercase tracking-[0.05em]">
              {m.detail}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
