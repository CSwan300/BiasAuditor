import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    // 1. Specifies the DOM environment
    environment: 'jsdom',
    // 2. Tells Vitest to run your setup file before every test
    setupFiles: ['./vitest.vitest.setup.ts'],
    // 3. Allows using 'describe', 'it', 'expect' without importing them
    globals: true,
  },
});