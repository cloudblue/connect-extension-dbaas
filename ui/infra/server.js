const webpack = require('webpack');
const WebpackDevServer = require('webpack-dev-server');

const webpackConfig = require('../../webpack.config');
const param = require('./param');


const host = param('host', '0.0.0.0');
const port = param('port', '80');


const server = new WebpackDevServer(
  {
    host,
    port,
    liveReload: true,
    allowedHosts: 'all',
    historyApiFallback: { index: '/' },
  },
  webpack(webpackConfig),
);


server.startCallback(() => {
  console.log(`Server started on: ${host}:${port}`);
});
