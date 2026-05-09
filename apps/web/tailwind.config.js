/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // MAMA-LENS brand palette — warm, calming, African-inspired
        primary: {
          50:  "#fdf4f0",
          100: "#fbe5d8",
          200: "#f6c9b0",
          300: "#f0a57f",
          400: "#e87a4d",
          500: "#e05a2b",  // Main brand orange
          600: "#c94420",
          700: "#a73419",
          800: "#882c18",
          900: "#6f2617",
        },
        secondary: {
          50:  "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",  // Health green
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
        },
        warm: {
          50:  "#fffbf5",
          100: "#fef3e2",
          200: "#fde4b9",
          300: "#fbd08a",
          400: "#f8b84e",
          500: "#f59e0b",  // Warm amber
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
        },
        calm: {
          50:  "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",  // Calm blue
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
        earth: {
          50:  "#faf7f2",
          100: "#f3ece0",
          200: "#e6d5be",
          300: "#d4b896",
          400: "#c09870",
          500: "#a97c52",  // Earth brown
          600: "#8b6340",
          700: "#6f4e32",
          800: "#5a3f29",
          900: "#4a3422",
        },
        emergency: {
          50:  "#fff1f2",
          100: "#ffe4e6",
          200: "#fecdd3",
          300: "#fda4af",
          400: "#fb7185",
          500: "#f43f5e",  // Emergency red
          600: "#e11d48",
          700: "#be123c",
          800: "#9f1239",
          900: "#881337",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Poppins", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },
      boxShadow: {
        "soft": "0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)",
        "card": "0 4px 24px -4px rgba(0, 0, 0, 0.08)",
        "glow-primary": "0 0 20px rgba(224, 90, 43, 0.3)",
        "glow-green": "0 0 20px rgba(34, 197, 94, 0.3)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 3s ease-in-out infinite",
        "slide-up": "slideUp 0.3s ease-out",
        "fade-in": "fadeIn 0.4s ease-out",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
