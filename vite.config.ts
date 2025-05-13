/// <reference types="vitest" />
import { resolve } from 'path';

import vue from '@vitejs/plugin-vue';
import eslint from 'vite-plugin-eslint';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { ConfigEnv, defineConfig, loadEnv } from 'vite';
import vuetify from 'vite-plugin-vuetify';
import { visualizer } from 'rollup-plugin-visualizer';

const axiosRedirectConfig = () => ({
  name: 'serverProxy',
  configureServer(server: any) {
    const filter = function filter(pathname: any, req: any) {
      return (
        typeof req.headers['x-df-axios'] !== 'undefined' || (
          pathname !== '/' &&
          !pathname.startsWith('/@') &&
          !pathname.startsWith('/vue') &&
          !pathname.startsWith('/node_modules')
        )
      );
      // return ;
    };
    server.middlewares.use(
      '/',
      createProxyMiddleware(filter, {
        target: process.env.VITE_AXIOS_TARGET,
        changeOrigin: false,
        pathRewrite: (path) => path,
      }),
    );
  },
});

export default ({ mode }: ConfigEnv) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd()) };
  return defineConfig({
    plugins: [
      vue(),
      // dts(),  // enable when TS errors are no longer present
      {
        ...eslint({
          failOnWarning: false,
          failOnError: false,
        }),
        apply: 'serve',
        enforce: 'post',
      },
      vuetify({ autoImport: true }),
      axiosRedirectConfig(),
      visualizer({
        open: false,
        filename: 'coverage/stats.html',
        gzipSize: true,
        brotliSize: true,
      }),
    ],
    resolve: {
      // alias: {
      // @ts-ignore
      // '~': fileURLToPath(new URL('./node_modules', import.meta.url)),
      // @ts-ignore
      // '@': fileURLToPath(new URL('./vue', import.meta.url)),
      // 'vue': 'vue/dist/vue.esm-bundler.js'
      // },
      extensions: [
        '.js',
        '.mjs',
        '.ts',
        '.vue',
        '.json',
        '.css',
      ],
    },
    server: {
      port: 8080,
      fs: { allow: ['..'] },
    },
    build: {
      target: 'es2015',
      sourcemap: true,
      lib: {
        entry: resolve(__dirname, 'vue/apps.ts'),
        formats: ['umd', 'es'],
        fileName: 'project-base',
        name: 'project-base',
      },
      rollupOptions: {
        external: [
          '@kyvg/vue3-notification',
          '@velis/dynamicforms',
          'axios',
          'browser-update',
          'lodash-es',
          'pinia',
          'slugify',
          /^vanilla-cookieconsent\/.*/,
          'vue',
          'vue-ionicon',
          'vue-multiselect',
          /^vuetify\/.*/,
          'vue3-cookies',
        ],
        output: {
          exports: 'named',
          globals: (id: string) => id, // all external modules are currently not aliased to anything but their own names
        },
      },
    },
    test: {
      server: {
        deps: {
          inline: [/vuetify/]
        },
      },
      globals: true,
      environment: 'jsdom',
      include: ['vue/**/*.spec.*'],
      exclude: ['**/*.css'],
    },
  });
};
