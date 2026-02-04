const typography = require("@tailwindcss/typography");

module.exports = {
  content: ["./src/**/*.css", "./src/**/*.svelte", "../../v1-3/examples/grid/*.json"],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            color: "var(--color-fg)",
            h1: {
              fontFamily: "var(--font-heading)",
              color: "var(--color-accent)",
            },
            h2: {
              fontFamily: "var(--font-heading)",
            },
          },
        },
      },
    },
  },
  plugins: [typography],
};
