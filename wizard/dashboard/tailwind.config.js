/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{svelte,js,ts}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
      },
      typography: () => ({
        DEFAULT: {
          css: {
            fontFamily: "var(--font-prose-body)",
            fontSize: "calc(1em * var(--scale-prose-body))",
            lineHeight: "1.65",
            color: "inherit",
            "h1,h2,h3,h4,h5,h6": {
              fontFamily: "var(--font-prose-title)",
              fontSize: "calc(1em * var(--scale-prose-title))",
            },
            "code, pre code": {
              fontFamily: "var(--font-code)",
              fontSize: "calc(0.95em * var(--scale-code))",
            },
            pre: {
              fontFamily: "var(--font-code)",
              fontSize: "calc(0.95em * var(--scale-code))",
            },
            "p, li": {
              fontFamily: "var(--font-prose-body), var(--font-emoji)",
            },
            "h1, h2, h3, h4, h5, h6": {
              fontFamily: "var(--font-prose-title), var(--font-emoji)",
            },
            "code, pre code, pre": {
              fontFamily: "var(--font-code), var(--font-emoji)",
            },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
