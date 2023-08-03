const path = require('path');

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
module.exports = {
  devServer: {
    https: true,
    host: 'localhost'
  },
  productionSourceMap: false,
  pluginOptions: {
    'style-resources-loader': {
      preProcessor: 'less',
      patterns: [path.resolve(__dirname, './src/components/ui/_vars.less')]
    },
    'svgSprite': {

      esModule: false,
      
      // The directory containing your SVG files.
      dir: 'src/assets/icons',

      // The reqex that will be used for the Webpack rule.
      test: /\.(svg)(\?.*)?$/,

      // @see https://github.com/kisenka/svg-sprite-loader#configuration
      loaderOptions: {
        extract: true,
        spriteFilename: 'img/icons.[hash:8].svg' // or 'img/icons.svg' if filenameHashing == false
      },

      // @see https://github.com/kisenka/svg-sprite-loader#configuration
      pluginOptions: {
        plainSprite: false
      }
    }
  },
  chainWebpack: config => {
    config.module
      .rule('svg-sprite')
      .use('svgo-loader')
      .loader('svgo-loader')
      .end();


    if (process.env.NODE_ENV != 'development') {
      const imgRule = config.module.rule('images');
      
      imgRule.uses.clear();
      imgRule
        .use('img-optimize-loader')
          .loader('img-optimize-loader')
            .options({
              compress: {
                mode: 'high',
                webp: true
              }
            });
    }
  }
}
