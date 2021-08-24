const path = require('path');

const libraryFileName = 'django-project-base';

module.exports = {
  outputDir: path.resolve(__dirname, `../static/${libraryFileName}/`),
  css: {
    extract: {
      ignoreOrder: true,
      filename: `css/${libraryFileName}.css`,
      chunkFilename: `css/${libraryFileName}-vendor.css`,
    },
  },
  configureWebpack: {
    resolve: {
      alias: {
        vue$: 'vue/dist/vue.esm.js',
        '@': path.resolve('src'),
      },
      extensions: ['.js', '.vue', '.json'],
    },
    devServer: {
      proxy: {
        '.*': {
          target: 'http://localhost:8000',
          secure: false,
        },
      },
    },
    plugins: [],
    output: {
      filename: `js/${libraryFileName}.js`,
      chunkFilename: `js/${libraryFileName}-vendors.js`,
    },
  },
};
