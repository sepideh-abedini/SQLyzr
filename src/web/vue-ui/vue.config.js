module.exports = {
    // The base URL where the app will be deployed
    publicPath: '/',

    // Output directory for the built files
    outputDir: '../static/vue',

    // Directory for static assets
    assetsDir: 'assets',

    productionSourceMap: false,
    lintOnSave: false,

    devServer: {
        proxy: {
            '/api': {
                target: 'http://localhost:7777',
                changeOrigin: true
            }
        }
    }
}