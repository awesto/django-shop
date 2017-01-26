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
			var params = $location.search(), attr = attrs['shopProductFilter'];
			if (!attr)
				throw new Error("Directive shop-attribute-filter requires an attribute.");

			scope.filters = scope.filters || {};
			if (params[attr]) {
				scope.filters[attr] = params[attr];
			}

			scope.filterChanged = function() {
				var params = {};
				if (scope.filters[attr]) {
					params[attr] = scope.filters[attr];
				}
				$location.search(params);
				scope.searchQuery = '';  // remove content in search field
				scope.$emit('shopCatalogFilter', params);
			};
		}
	};
}]);


})(window.angular);
