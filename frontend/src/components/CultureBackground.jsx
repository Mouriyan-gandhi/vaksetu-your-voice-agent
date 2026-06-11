"use client";
import { useEffect, useRef } from "react";
import { useTheme } from "./ThemeProvider";

const GLYPHS = [
  "अ", "इ", "क", "श", // Hindi/Sanskrit
  "க", "உ", "ழ", "வ", // Tamil
  "అ", "ఇ", "క", "వ", // Telugu
  "അ", "ഇ", "ക", "മ", // Malayalam
  "ಅ", "ಇ", "ಕ", "ವ", // Kannada
  "অ", "ই", "ক", "ব", // Bengali
  "અ", "ઇ", "ક", "વ", // Gujarati
  "ੳ", "ਅ", "ਕ", "ਵ", // Punjabi
  "ଅ", "ଇ", "କ", "ବ", // Odia
];

export default function CultureBackground() {
  const canvasRef = useRef(null);
  const { theme } = useTheme();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    let width, height;
    const particles = [];
    const glyphs = [];
    const particleCount = 15;
    const glyphCount = 12;
    const maxDistance = 400;

    let mouseX = 0;
    let mouseY = 0;

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };

    const handleMouseMove = (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    const getThemeColors = () => {
      const isLight = document.documentElement.classList.contains("light");
      return {
        accent: isLight ? "rgba(249, 115, 22, 0.4)" : "rgba(249, 115, 22, 0.2)",
        glyph: isLight ? "rgba(0, 0, 0, 0.04)" : "rgba(255, 255, 255, 0.03)",
        line: isLight ? "rgba(0, 0, 0, 0.03)" : "rgba(255, 255, 255, 0.02)",
        spot: isLight ? "rgba(253, 186, 116, 0.15)" : "rgba(249, 115, 22, 0.1)"
      };
    };

    class Particle {
      constructor() {
        this.init();
      }
      init() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.3;
        this.vy = (Math.random() - 0.5) * 0.3;
        this.radius = Math.random() * 2 + 0.5;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;
        const dx = mouseX - this.x;
        const dy = mouseY - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 300) {
          this.x += dx * 0.005;
          this.y += dy * 0.005;
        }
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
      }
    }

    class Glyph {
      constructor() {
        this.init();
      }
      init() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.text = GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
        this.size = Math.random() * 40 + 20;
        this.vx = (Math.random() - 0.5) * 0.1;
        this.vy = (Math.random() - 0.5) * 0.1;
        this.opacity = Math.random() * 0.5 + 0.2;
        this.rotation = Math.random() * Math.PI * 2;
        this.rotSpeed = (Math.random() - 0.5) * 0.002;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.rotation += this.rotSpeed;
        if (this.x < -100) this.x = width + 100;
        if (this.x > width + 100) this.x = -100;
        if (this.y < -100) this.y = height + 100;
        if (this.y > height + 100) this.y = -100;
      }
      draw() {
        const colors = getThemeColors();
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);
        ctx.font = `${this.size}px 'DM Serif Display', serif`;
        ctx.fillStyle = colors.glyph;
        ctx.fillText(this.text, 0, 0);
        ctx.restore();
      }
    }

    const init = () => {
      resize();
      for (let i = 0; i < particleCount; i++) particles.push(new Particle());
      for (let i = 0; i < glyphCount; i++) glyphs.push(new Glyph());
    };

    const animate = () => {
      ctx.clearRect(0, 0, width, height);
      const colors = getThemeColors();

      // Mesh
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < maxDistance) {
            ctx.strokeStyle = colors.line;
            ctx.lineWidth = (1 - dist / maxDistance) * 0.5;
            ctx.beginPath();ctx.moveTo(particles[i].x, particles[i].y);ctx.lineTo(particles[j].x, particles[j].y);ctx.stroke();
          }
        }
        particles[i].update();
      }

      // Glyphs
      glyphs.forEach(g => {
        g.update();
        g.draw();
      });

      // Mouse Spotlight
      const grad = ctx.createRadialGradient(mouseX, mouseY, 0, mouseX, mouseY, 600);
      grad.addColorStop(0, colors.spot);
      grad.addColorStop(1, "transparent");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      animationFrameId = requestAnimationFrame(animate);
    };

    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", handleMouseMove);
    init();
    animate();

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [theme]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 bg-background pointer-events-none transition-colors duration-700"
    />
  );
}
