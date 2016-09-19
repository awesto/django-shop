(function(angular, undefined) {
'use strict';

var Module = angular.module('myshop.filter', []);

Module.directive('shopAttributeFilter', ['$location', '$timeout', function($location, $timeout) {
	return {
		link: function(scope, element, attrs) {
			var params = $location.search(), attr = attrs['shopAttributeFilter'];
			if (!attr)
				throw new Error("Directive shop-attribute-filter requires an attribute.");
			if (angular.isDefined(params[attr])) {
				$timeout(function() {
					// delay until next digest cycle
					scope.$emit('shopCatalogFilter', params);
				});
				scope[attr] = params[attr];
			}

			scope.filterChanged = function() {
				console.log(scope);
				if (scope[attr]) {
					params[attr] = scope[attr];
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
