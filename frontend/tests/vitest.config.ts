import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    // Sync this filename with your actual file in the root
    setupFiles: ['./vitest.setup.ts'],
    globals: true,
  },
});