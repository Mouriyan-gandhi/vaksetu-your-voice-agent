"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "./ThemeProvider";

const navLinks = [
  { name: "Build", href: "/build" },
  { name: "Analysis", href: "/analysis" },
  { name: "Intelligence", href: "/healthcare" },
  { name: "Finance", href: "/banking" },
  { name: "Platform", href: "/platform" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { theme, toggle } = useTheme();
  const { scrollY } = useScroll();
  
  const background = useTransform(
    scrollY,
    [0, 100],
    ["rgba(255, 255, 255, 0)", "rgba(255, 255, 255, 0.05)"]
  );

  return (
    <motion.nav 
      style={{ backgroundColor: background }}
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-border transition-all duration-500"
    >
      <div className="max-w-7xl mx-auto px-6 h-16 md:h-20 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-4 group">
          <div className="w-10 h-10 rounded-full bg-saffron flex items-center justify-center text-black font-bold text-lg shadow-lg group-hover:scale-110 transition-transform">V</div>
          <span className="font-display text-2xl md:text-3xl tracking-tighter text-foreground group-hover:text-saffron transition-colors">
            VaakSetu
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center space-x-12">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className="text-xs font-mono uppercase tracking-[0.2em] text-muted hover:text-foreground transition-all"
            >
              {link.name}
            </Link>
          ))}
        </div>

        {/* Right side */}
        <div className="hidden md:flex items-center space-x-6">
          <button
            onClick={toggle}
            className="w-10 h-10 rounded-full border border-border flex items-center justify-center text-muted hover:text-foreground hover:bg-surface-hover transition-all"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <Link href="/platform" className="bg-foreground text-background px-6 py-2.5 rounded-full text-xs font-semibold hover:opacity-90 transition-all">
            Get Started
          </Link>
        </div>

        {/* Mobile toggle */}
        <button onClick={() => setOpen(!open)} className="md:hidden p-2 text-foreground">
          {open ? "✕" : "☰"}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden glass-card mx-6 my-4 p-8 space-y-6 border border-border bg-background/95 backdrop-blur-2xl"
        >
          {navLinks.map((link) => (
            <Link key={link.name} href={link.href} onClick={() => setOpen(false)}
              className="block text-2xl font-display text-foreground">
              {link.name}
            </Link>
          ))}
          <button onClick={toggle} className="w-full text-left font-mono text-xs uppercase tracking-widest text-muted">
            {theme === "dark" ? "Switch to Light" : "Switch to Dark"}
          </button>
        </motion.div>
      )}
    </motion.nav>
  );
}
