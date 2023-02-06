import { defineConfig } from 'vite';

import { fileURLToPath, URL as URL_ } from 'node:url';

import { createProxyMiddleware } from 'http-proxy-middleware';
import eslintPlugin from 'vite-plugin-eslint';
import vuePlugin from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';

const axiosRedirectConfig = () => ({
  name: 'serverProxy',
  configureServer(server: any) {
    const filter = function filter(pathname: any, req: any) {
      return typeof req.headers['x-df-axios'] !== 'undefined';
    };
    server.middlewares.use(
      '/',
      createProxyMiddleware(filter, {
        target: 'http://localhost:8000',
        changeOrigin: false,
        pathRewrite: (path) => {
          // console.log('path', path);
          return path;
        },
      }),
    );
  },
});


export default defineConfig({
  plugins: [
    vuePlugin(),
    {
      ...eslintPlugin({
        failOnWarning: false,
        failOnError: false,
      }),
      apply: 'serve',
      enforce: 'post',
    },
    vuetify({ autoImport: true }),
    axiosRedirectConfig()
  ],
  resolve: {
    alias: {
      "~": fileURLToPath(new URL_('./node_modules', import.meta.url)),
      "@": fileURLToPath(new URL_('./vue', import.meta.url)),
    },
    extensions: [
      '.js',
      '.ts',
      '.vue',
      '.json',
      '.css'
    ]
  },
  server: {
    port: 8080,
    fs: {
      allow: ['..'],
    }
  }
})
