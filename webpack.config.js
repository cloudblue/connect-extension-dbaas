/* eslint-disable import/no-unresolved */
const path = require('path');
const param = require('./ui/infra/param');
const webpack = require('webpack');

const HtmlWebpackPlugin = require('html-webpack-plugin');
const CircularDependencyPlugin = require('circular-dependency-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { VueLoaderPlugin } = require('vue-loader');
const ESLintPlugin = require('eslint-webpack-plugin');


const production = Boolean(param('production', false));
const title = param('title', '');
const publicPath = param('output', 'output');


const webpackConfig = {
  mode: production ? 'production' : 'development',

  entry: ['./ui/app/app'],

  output: {
    filename: '[contenthash].js',
    path: path.resolve(__dirname, publicPath),
    clean: true,
  },

  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        include: [path.resolve(__dirname, 'ui/app')],
        exclude: [/node_modules/, /\.spec.js/, /test-tools/],
      },
      {
        test: /\.styl(us)?$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'stylus-loader',
        ],
      },
      {
        test: /\.pug$/,
        loader: 'pug-plain-loader',
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: 'svg-sprite-loader',
            options: {
              spriteFilename: '[hash:20].svg',
              symbolId: '[folder]_[name]_[hash:6]',
            },
          },
        ],
      },
    ],
  },

  plugins: [
    new VueLoaderPlugin(),

    new ESLintPlugin({
      extensions: ['js', 'vue'],
    }),

    new HtmlWebpackPlugin({
      template: 'ui/index.html',
      filename: 'index.html',

      templateParameters: {
        title,
        publicPath,
      },
    }),

    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[id].css',
    }),

    new CircularDependencyPlugin({
      exclude: /node_modules/,
      include: /(.*\.vue)|(.*\.js)/,
      failOnError: true,
      allowAsyncCycles: false,
      cwd: process.cwd(),
    }),

    new webpack.ProgressPlugin(),
  ],

  resolve: {
    fallback: {
      buffer: require.resolve('buffer'),
    },

    alias: {
      vue$: path.resolve(__dirname, 'node_modules/vue/dist/vue.esm.js'),
      '@': path.resolve(__dirname, 'ui/app'),
      rest: path.resolve(__dirname, 'ui/app/tools/rest'),
      '~tools': path.resolve(__dirname, 'ui/app/tools'),
      '~utils': path.resolve(__dirname, 'ui/app/tools/utils'),
      '~helpers': path.resolve(__dirname, 'ui/app/tools/helpers'),
      '~constants': path.resolve(__dirname, 'ui/app/tools/constants'),
      '~mixins': path.resolve(__dirname, 'ui/app/tools/mixins'),
      '~views': path.resolve(__dirname, 'ui/app/views'),
      '~components': path.resolve(__dirname, 'ui/app/components'),
      '~styles': path.resolve(__dirname, 'ui/app/styles'),
      '~api': path.resolve(__dirname, 'ui/app/api'),
    },
  },

  cache: production ? false : {
    type: 'filesystem',
    allowCollectingMemory: true,
  },

  performance: {
    hints: false,
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },

  devtool: production ? false : 'eval-cheap-module-source-map',
  optimization: {
    sideEffects: true,
    minimize: production,
  },
};


module.exports = webpackConfig;
