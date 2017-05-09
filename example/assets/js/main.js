var angular = require('angular');
var djangoShopDashboard = angular.module('djangoShopDashboard', [require('ng-admin')]);

/*
djangoShopDashboard.config(['$locationProvider', function($locationProvider) {
	$locationProvider.html5Mode({
		enabled: true,
		requireBase: false,
		rewriteLinks: false
	});
}]);
*/

djangoShopDashboard.config(['$httpProvider', 'NgAdminConfigurationProvider', 'FieldViewConfigurationProvider', function(http, nga, fvp) {
	http.defaults.headers.common['X-CSRFToken'] = '{{ csrf_token }}';
	nga.registerFieldType('amount', require('./types/AmountField'));
	fvp.registerFieldView('amount', require('./types/AmountFieldView'));
}]);
