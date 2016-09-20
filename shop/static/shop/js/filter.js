(function(angular, undefined) {
'use strict';

var Module = angular.module('shop.filter', []);

// Directive <ANY shop-product-filter="attribute"> to be used to communicate selected
// attributes used to narrow down the list of products.
Module.directive('shopProductFilter', ['$location', '$timeout', function($location, $timeout) {
	return {
		link: function(scope, element, attrs) {
			var params = $location.search(), attr = attrs['shopProductFilter'];
			if (!attr)
				throw new Error("Directive shop-attribute-filter requires an attribute.");

			scope.filters = scope.filters || {};
			if (params[attr]) {
				$timeout(function() {
					// delay until next digest cycle
					scope.$emit('shopCatalogFilter', params);
				});
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
