"use client";
import { motion } from "framer-motion";

export default function ScrollReveal({ children, delay = 0, width = "100%", className = "" }) {
  return (
    <div 
      className={`${className} ${width === "100%" ? "w-full" : ""}`} 
      style={{ position: "relative" }}
    >
      <motion.div
        variants={{
          hidden: { opacity: 0, y: 75 },
          visible: { opacity: 1, y: 0 },
        }}
        initial="hidden"
        whileInView="visible"
        transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
        viewport={{ once: true }}
        className="h-full w-full"
      >
        {children}
      </motion.div>
    </div>
  );
}
