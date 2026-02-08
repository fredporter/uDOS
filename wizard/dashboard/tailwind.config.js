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
        accent: "var(--theme-accent, #38bdf8)",
        surface: {
          DEFAULT: "var(--theme-surface, #0f172a)",
        },
      },
      typography: () => ({
        DEFAULT: {
          css: {
            fontFamily: "var(--font-prose-body)",
            lineHeight: "var(--prose-line-height)",
            color: "inherit",
            "h1,h2,h3,h4,h5,h6": {
              fontFamily: "var(--font-prose-title)",
            },
            h1: {
              fontSize: "calc(var(--prose-h1) * var(--scale-prose-title))",
            },
            h2: {
              fontSize: "calc(var(--prose-h2) * var(--scale-prose-title))",
            },
            h3: {
              fontSize: "calc(var(--prose-h3) * var(--scale-prose-title))",
            },
            h4: {
              fontSize: "calc(var(--prose-h4) * var(--scale-prose-title))",
            },
            h5: {
              fontSize: "calc(var(--prose-h5) * var(--scale-prose-title))",
            },
            h6: {
              fontSize: "calc(var(--prose-h6) * var(--scale-prose-title))",
            },
            "code, pre code": {
              fontFamily: "var(--font-code)",
            },
            pre: {
              fontFamily: "var(--font-code)",
            },
            "code, pre code, pre": {
              fontSize:
                "calc(var(--prose-body-size) * var(--scale-prose-body))",
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
            body: {
              fontSize:
                "calc(var(--prose-body-size) * var(--scale-prose-body))",
            },
            p: {
              fontSize:
                "calc(var(--prose-body-size) * var(--scale-prose-body))",
            },
            li: {
              fontSize:
                "calc(var(--prose-body-size) * var(--scale-prose-body))",
            },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
