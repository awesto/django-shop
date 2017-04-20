(function(angular, undefined) {
'use strict';

var Module = angular.module('django.shop.filter', []);

// Directive <form shop-product-filter="attribute"> to be used to communicate selected
// attributes used to narrow down the list of products.
Module.directive('shopProductFilter', ['$location', function($location) {
	return {
		require: 'form',
		restrict: 'AC',
		link: function(scope, element, attrs) {
			var params = $location.search(), filter_attrs;
			if (angular.isUndefined(attrs['shopProductFilter']))
				throw new Error("Directive shop-attribute-filter requires an attribute.");
			filter_attrs = scope.$eval(attrs['shopProductFilter']) || [attrs['shopProductFilter']];

			scope.filters = scope.filters || {};
			angular.forEach(filter_attrs, function(attr) {
				if (params[attr]) {
					scope.filters[attr] = params[attr];
				}
			});

			scope.filterChanged = function() {
				var params = {};
				angular.forEach(filter_attrs, function(attr) {
					if (scope.filters[attr]) {
						params[attr] = scope.filters[attr];
					}
				});
				scope.searchQuery = '';  // remove content in search field
				scope.$emit('shopCatalogFilter', params);
			};
		}
	};
}]);


})(window.angular);
