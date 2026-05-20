import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // CRITICAL: Ensures paths like /assets/ become ./assets/
  server: {
    port: 3000,
    host: true // Allows the server to be accessible outside the container
  },
  build: {
    outDir: 'dist', // Ensures the output folder matches your Dockerfile COPY command
    emptyOutDir: true,
  }
})