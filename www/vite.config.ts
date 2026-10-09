import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('arcgis-') || tag.startsWith('calcite-')
        }
      }
    }),
    vueDevTools(),
  ],
  optimizeDeps: {
    include: ['@arcgis/core']
  },
  build: {
    target: 'es2022',
    chunkSizeWarningLimit: 2000
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
