var angular = require('angular');
var djangoShopDashboard = angular.module('djangoShopDashboard');

djangoShopDashboard.config(['NgAdminConfigurationProvider', 'FieldViewConfigurationProvider', function(nga, fvp) {
	nga.registerFieldType('amount', require('./types/AmountField'));
	fvp.registerFieldView('amount', require('./types/AmountFieldView'));
}]);
