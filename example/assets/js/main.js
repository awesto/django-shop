var angular = require('angular');
var djangoShopDashboard = angular.module('djangoShopDashboard', [require('ng-admin')]);

/*
djangoShopDashboard.config(['$locationProvider', function(locationProvider) {
	locationProvider.html5Mode({
		enabled: true,
		requireBase: false,
		rewriteLinks: false
	});
}]);
*/

djangoShopDashboard.config(['NgAdminConfigurationProvider', 'FieldViewConfigurationProvider', function(nga, fvp) {
	nga.registerFieldType('amount', require('./types/AmountField'));
	fvp.registerFieldView('amount', require('./types/AmountFieldView'));
}]);
