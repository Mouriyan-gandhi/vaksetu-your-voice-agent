"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const scripts = [
  { text: "वाक्", lang: "Hindi" },
  { text: "ವಾಕ್", lang: "Kannada" },
  { text: "வாக்", lang: "Tamil" },
  { text: "వాక్", lang: "Telugu" },
  { text: "বাক্", lang: "Bengali" },
  { text: "વાક્", lang: "Gujarati" },
  { text: "ਵਾਕ", lang: "Punjabi" },
  { text: "വാക്", lang: "Malayalam" },
  { text: "ବାକ୍", lang: "Odia" },
];

export default function DynamicLogo() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % scripts.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center">
      <div className="flex items-baseline justify-center space-x-3 relative min-h-[1.8em] md:min-h-[1.6em]">
        <AnimatePresence mode="wait">
          <motion.span
            key={index}
            initial={{ y: 80, opacity: 0, filter: "blur(20px)" }}
            animate={{ y: 0, opacity: 1, filter: "blur(0px)" }}
            exit={{ y: -80, opacity: 0, filter: "blur(20px)" }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-gradient-saffron font-display text-[3.5em] md:text-[5rem] font-normal leading-none"
          >
            {scripts[index].text}
          </motion.span>
        </AnimatePresence>
        <span className="font-display text-foreground font-normal text-[3.5em] md:text-[5rem] leading-none">Setu</span>
      </div>
      <motion.p 
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        className="text-[10px] md:text-sm uppercase tracking-[0.5em] mt-4 font-mono font-bold"
      >
        BRIDGING VOICES · BUILT FOR BHARAT
      </motion.p>
    </div>
  );
}
