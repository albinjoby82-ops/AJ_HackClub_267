import { defineConfig } from 'vite';

export default defineConfig({
  server: { port: 5183, strictPort: true },
  preview: { port: 5183, strictPort: true },
  build: { assetsInlineLimit: 0 },
});
