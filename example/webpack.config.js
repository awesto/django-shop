var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
	context: __dirname,
	entry: './assets/js/index',
	output: {
		path: path.resolve('../workdir/webpack_bundles/'),
		filename: "[name]-[hash].js"
	},
	module: {
        loaders: [
            { test: /\.js$/, loader: 'babel-loader' },
            { test: /\.html$/, loader: 'html-loader' },
        ],
	},
	plugins: [
		new BundleTracker({
			filename: '../workdir/webpack_bundles/webpack-stats.json'
		}),
	],
    externals: {
        'text-encoding': 'window'
    }
}

/*

module.exports = {
  entry: './app/assets/frontend/main.jsx',
  output: {
    path: __dirname + '/app/assets/javascripts',
    filename: 'bundle.js'
  },
  resolve: {
    extensions: ['', '.js', '.jsx']
  },
}
*/
