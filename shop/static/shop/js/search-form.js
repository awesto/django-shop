(function() {
'use strict';

//module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.search', ['django.shop.utils']);

// Directive <form shop-product-search ...> to be used in the form containing the input field
// for entering the search query
djangoShopModule.directive('shopProductSearch', ['$location', '$timeout', 'djangoShop', function($location, $timeout, djangoShop) {
	return {
		require: 'form',
		restrict: 'AC',
		controller: ['$scope', function($scope) {
			var acPromise = null;

			// handle typeahead using autocomplete
			$scope.autocomplete = function() {
				var config;
				if (!angular.isString($scope.searchQuery) || $scope.searchQuery.length < 3) {
					config = null;
					$location.search({});
				} else {
					config = {
						params: {
							q: $scope.searchQuery
						}
					};
					$scope.property_filters = [];
					$location.search(config.params);
				}
				// delay the execution of reloading products
				if (acPromise) {
					$timeout.cancel(acPromise);
					acPromise = null;
				}
				acPromise = $timeout(function() {
					$scope.$emit('shopCatalogSearch', config);
				}, 666);
			};
		}],
		link: function(scope, element, attrs, formController) {
			var queries = {params: $location.search()};

			// convert query string from URL to object
			if (angular.equals({}, queries.params)) {
				queries = djangoShop.paramsFromSearchQuery();
				scope.searchQuery = queries.q;
			} else {
				$timeout(function() {
					// delay until next digest cycle
					scope.$emit('shopCatalogSearch', queries);
				});
				scope.searchQuery = queries.params.q;
			}

			// handle classic search through submission form
			scope.submitSearch = function() {
				if (scope.searchQuery.length > 1) {
					element[0].submit();
				}
			};
		}
	};
}]);

})();
