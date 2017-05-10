// compile all JS files using
// ./node_modules/.bin/webpack --config webpack.config.js --watch

var BundleTracker = require('webpack-bundle-tracker');
var path = require('path');

module.exports = {
	entry: [
		'./assets/js/main.js',
	],
	output: {
		path: path.resolve('../workdir/webpack_bundles/'),
		filename: "[name]-[hash].js"
	},
	module: {
		loaders: [
			{ test: /\.js$/, loader: 'babel', query: {compact: false}, exclude: /node_modules\/(?!admin-config)/ },
			{ test: /\.html$/, loader: 'html' },
			{ test: /\.(woff2?|svg|ttf|eot)(\?.*)?$/, loader: 'url' },
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
};
