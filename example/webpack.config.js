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
	plugins: [
		new BundleTracker({filename: '../workdir/webpack_bundles/webpack-stats.json'})
	]
}
