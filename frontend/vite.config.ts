import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

/**
 * Vite Configuration
 * Includes Vitest settings for React Testing Library and JSDOM
 * https://vitejs.dev/config/
 */
export default defineConfig({
  plugins: [react()],

  // Base path for deployment (ensures relative asset paths)
  base: './',

  server: {
    port: 3000,
    host: true // Necessary for Docker/Container access
  },

  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },

  test: {
    // Enables global functions like 'describe', 'it', and 'expect'
    globals: true,

    // Simulates a browser environment in Node.js
    environment: 'jsdom',

    setupFiles: ['./tests/vitest.setup.ts'],

    include: ['tests/**/*.{test,spec}.{ts,tsx}'],

    exclude: ['node_modules', 'dist'],
  },
});