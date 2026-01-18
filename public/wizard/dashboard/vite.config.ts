import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [tailwindcss(), svelte()],
  root: 'src',
  build: {
    outDir: '../dist',
    target: 'es2020',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    open: false
  }
});
