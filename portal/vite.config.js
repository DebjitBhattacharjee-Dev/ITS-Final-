import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8080,
    proxy: getProxyOptions(),
  },
  build: {
    outDir: path.resolve(__dirname, '../its_ui_redesign/public/portal'),
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'index.css'
          }
          return 'assets/[name]-[hash][extname]'
        },
      },
    },
  },
})

function getProxyOptions() {
  const config = getCommonSiteConfig()
  const webserver_port = config ? config.webserver_port : 8000
  return {
    '^/(app|login|api|assets|files|private)': {
      target: `http://127.0.0.1:${webserver_port}`,
      ws: true,
      router: function (req) {
        const site_name = req.headers.host.split(':')[0]
        return `http://${site_name}:${webserver_port}`
      },
    },
  }
}

function getCommonSiteConfig() {
  let currentDir = path.resolve('.')
  while (currentDir !== '/') {
    if (
      fs.existsSync(path.join(currentDir, 'sites')) &&
      fs.existsSync(path.join(currentDir, 'apps'))
    ) {
      let configPath = path.join(currentDir, 'sites', 'common_site_config.json')
      if (fs.existsSync(configPath)) {
        return JSON.parse(fs.readFileSync(configPath))
      }
      return null
    }
    currentDir = path.resolve(currentDir, '..')
  }
  return null
}
