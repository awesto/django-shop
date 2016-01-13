(function() {
'use strict';

//module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.search', []);

// Directive <form shop-product-search ...> to be used in the form containing the input field
// for entering the search query
djangoShopModule.directive('shopProductSearch', ['$window', '$location', function($window, $location) {
	return {
		require: 'form',
		restrict: 'AC',
		controller: ['$scope', '$timeout', function($scope, $timeout) {
			var acPromise = null;

			// handle autocomplete
			$scope.autocomplete = function() {
				var config;
				if ($scope.searchQuery.length < 3) {
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
			var i, splitted, queries = {params: $location.search()};

			// convert query string from URL to object
			if (angular.equals({}, queries.params)) {
				scope.searchQuery = '';
				queries = $window.location.search.replace(/^\?/, '').split('&');
				for (i = 0; i < queries.length; i++) {
					splitted = queries[i].split('=');
					if (splitted[0] === 'q') {
						scope.searchQuery = decodeURIComponent(splitted[1].split('+').join('%20'));
					}
				}
			} else {
				scope.searchQuery = queries.params.q;
				scope.autocomplete();
			}

			// handle classic search submission through form
			scope.submitSearch = function() {
				if (scope.searchQuery.length > 1) {
					element[0].submit();
				}
			};

		}
	};
}]);

})();
