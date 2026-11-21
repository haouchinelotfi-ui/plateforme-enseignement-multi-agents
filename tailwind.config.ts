import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef6ff",
          100: "#d9eaff",
          200: "#bcd9ff",
          300: "#8ec0ff",
          400: "#599cff",
          500: "#3478f6",
          600: "#1f5ce0",
          700: "#1a48b8",
          800: "#1b3e91",
          900: "#1c3773",
        },
        ink: {
          50: "#f6f7f9",
          100: "#eceef2",
          200: "#d5dae3",
          300: "#b0bac9",
          400: "#8595ad",
          500: "#677691",
          600: "#525f76",
          700: "#434d60",
          800: "#3a4251",
          900: "#1e2330",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.6s ease-out forwards",
        "fade-up": "fadeUp 0.6s ease-out forwards",
        "slide-down": "slideDown 0.3s ease-out forwards",
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "bounce-subtle": "bounceSubtle 2s ease-in-out infinite",
        "gradient": "gradient 8s linear infinite",
        "blob": "blob 12s ease-in-out infinite",
        "shimmer": "shimmer 2s linear infinite",
        "float": "float 6s ease-in-out infinite",
        "marquee": "marquee 40s linear infinite",
        "scale-in": "scaleIn 0.4s ease-out forwards",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        fadeUp: { "0%": { opacity: "0", transform: "translateY(20px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideDown: { "0%": { opacity: "0", transform: "translateY(-10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        bounceSubtle: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-6px)" } },
        gradient: { "0%,100%": { "background-position": "0% 50%" }, "50%": { "background-position": "100% 50%" } },
        blob: {
          "0%,100%": { transform: "translate(0,0) scale(1)" },
          "33%": { transform: "translate(30px,-50px) scale(1.1)" },
          "66%": { transform: "translate(-20px,20px) scale(0.9)" },
        },
        shimmer: { "0%": { "background-position": "-1000px 0" }, "100%": { "background-position": "1000px 0" } },
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-12px)" } },
        marquee: { "0%": { transform: "translateX(0)" }, "100%": { transform: "translateX(-50%)" } },
        scaleIn: { "0%": { opacity: "0", transform: "scale(0.95)" }, "100%": { opacity: "1", transform: "scale(1)" } },
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(to right, rgba(120,120,140,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(120,120,140,0.08) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
