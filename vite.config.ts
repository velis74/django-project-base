import { ConfigEnv, defineConfig, loadEnv } from 'vite';

import { fileURLToPath, URL } from 'node:url';
import { resolve } from 'path';

import { createProxyMiddleware } from 'http-proxy-middleware';
import eslintPlugin from 'vite-plugin-eslint';
import vuePlugin from '@vitejs/plugin-vue';
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify';

const axiosRedirectConfig = () => ({
  name: 'serverProxy',
  configureServer(server: any) {
    const filter = function filter(pathname: any, req: any) {
      return (
        typeof req.headers['x-df-axios'] !== 'undefined'
        || (
          pathname !== '/'
          && !pathname.startsWith('/@')
          && !pathname.startsWith('/vue')
          && !pathname.startsWith('/node_modules')
        )
      );
      // return ;
    };
    server.middlewares.use(
      '/',
      createProxyMiddleware(filter, {
        target: process.env.VITE_AXIOS_TARGET,
        changeOrigin: false,
        pathRewrite: (path) => {
          return path;
        },
      }),
    );
  },
});

export default ({ mode }: ConfigEnv) => {
    process.env = {...process.env, ...loadEnv(mode, process.cwd())};
    return defineConfig({
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
            vuetify({autoImport: true}),
            axiosRedirectConfig()
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
            },
            host: 'django-project-base.org'
        },
        build: {
            target: 'es2015',
            lib: {
                entry: resolve(__dirname, 'vue/apps.ts'),
                formats: ['umd', 'es'],
                fileName: 'project-base',
                name: 'project-base'
            },
            rollupOptions: {
                external: ['@velis/dynamicforms', 'axios', 'lodash', 'pinia', 'vue', 'vue-ionicon', 'vuetify'],
                output: {
                    exports: 'named',
                    globals: (id: string) => id, // all external modules are currently not aliased to anything but their own names
                }
            }
        }
    });
};
