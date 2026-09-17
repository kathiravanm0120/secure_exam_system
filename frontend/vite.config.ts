import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/questions': 'http://127.0.0.1:8000',
      '/exams': 'http://127.0.0.1:8000',
      '/security': 'http://127.0.0.1:8000',
      '/blockchain': 'http://127.0.0.1:8000',
      '/identity': 'http://127.0.0.1:8000',
      '/fingerprints': 'http://127.0.0.1:8000',
      '/investigation': 'http://127.0.0.1:8000',
      '/dashboard': 'http://127.0.0.1:8000',
    },
  },
});
