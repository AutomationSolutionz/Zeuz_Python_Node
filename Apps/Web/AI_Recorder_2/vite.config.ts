import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: true,
        rollupOptions: {
      onLog(level, log, handler) {
        if (log.cause ) {
          // console.log(typeof(log.cause), Object.keys(log.cause) , log.cause)
          return
        }
        handler(level, log)
      }
    }
  },
})
