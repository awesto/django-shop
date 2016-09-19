(function(angular, undefined) {
'use strict';

var Module = angular.module('myshop.filter', []);

Module.directive('shopAttributeFilter', ['$location', '$timeout', function($location, $timeout) {
	return {
		link: function(scope, element, attrs) {
			var params = $location.search(), attr = attrs['shopAttributeFilter'];
			if (!attr)
				throw new Error("Directive shop-attribute-filter requires an attribute.");

			scope.filters = scope.filters || {};
			if (angular.isDefined(params[attr])) {
				$timeout(function() {
					// delay until next digest cycle
					scope.$emit('shopCatalogFilter', params);
				});
				scope.filters[attr] = params[attr];
			}

			scope.filterChanged = function() {
				if (scope.filters[attr]) {
					params[attr] = scope.filters[attr];
				} else {
					params = {};
				}
				$location.search(params);
				scope.searchQuery = '';  // remove content in search field
				scope.$emit('shopCatalogFilter', params);
			};
		}
	};
}]);


})(window.angular);
