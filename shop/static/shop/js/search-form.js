(function() {
'use strict';

//module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.search', ['django.shop.utils']);

// Directive <form shop-product-search ...> to be used in the form containing the input field
// for entering the search query
djangoShopModule.directive('shopProductSearch', ['$location', '$timeout', 'djangoShop',
                           function($location, $timeout, djangoShop) {
	return {
		require: 'form',
		restrict: 'AC',
		controller: ['$scope', function($scope) {
			var acPromise = null;

			// handle typeahead search using autocomplete
			$scope.autocomplete = function() {
				var params;
				if (!angular.isString($scope.searchQuery) || $scope.searchQuery.length < 3) {
					params = null;
					$location.search({});
				} else {
					params = {
						q: $scope.searchQuery
					};
					$scope.filters = {};  // remove content in filters
					$location.search(params);
				}
				// delay the execution of reloading products
				if (acPromise) {
					$timeout.cancel(acPromise);
				}
				acPromise = $timeout(function() {
					$scope.$emit('shop.catalog.search', params);
				}, 666);
			};
		}],
		link: function(scope, element, attrs, formController) {
			var params = $location.search();

			if (angular.equals({}, params)) {
				// convert URL ending in ?q=<query> into string for our search input field
				scope.searchQuery = djangoShop.paramsFromSearchQuery()['q'];
			} else if (params.q) {
				// we are performing an autocomplete search
				scope.searchQuery = params.q;
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
