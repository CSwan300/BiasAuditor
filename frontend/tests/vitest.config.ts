import { defineConfig } from 'vitest/config'; // Changed from 'vite' to 'vitest/config'
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Ensures paths like /assets/ become ./assets/
  server: {
    port: 3000,
    host: true // Allows the server to be accessible outside the container
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    // Ensure this matches the renamed file: vitest.setup.ts
    setupFiles: ['./vitest.setup.ts'],
    // This tells Vitest where to find your test files
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
  },
});