import { defineConfig } from 'vite';

export default defineConfig({
  base: './', // Ensures assets are resolved relatively in Electron file:/// environment
  server: {
    port: 5173,
    strictPort: true
  },
  build: {
    emptyOutDir: false
  }
});
