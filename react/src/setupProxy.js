const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = app => {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://python-flask:5000',
      // changeOrigin: true,
      pathRewrite: { '^/api': '' }
    })
  );
};