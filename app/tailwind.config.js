/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,svelte}',
    './src-tauri/**/*.{js,ts}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        humanist: ['Seravek', 'Gill Sans Nova', 'Ubuntu', 'Calibri', 'DejaVu Sans', 'sans-serif'],
        serif: ['ui-serif', 'Georgia', 'Cambria', 'Times New Roman', 'serif'],
        'old-style': ['Iowan Old Style', 'Palatino Linotype', 'URW Palladio L', 'P052', 'serif'],
        mono: ['JetBrains Mono', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Courier New', 'monospace'],
      },
      colors: {
        // uDOS brand colors
        brand: {
          50: '#f8f7ff',
          100: '#ede9fe',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
        },
      },
      spacing: {
        'safe': 'max(env(safe-area-inset-left), 0px)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
