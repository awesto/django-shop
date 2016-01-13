(function() {
'use strict';

//module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.search', []);

// Directive <form shop-product-search ...> to be used in the form containing the input field
// for entering the search query
djangoShopModule.directive('shopProductSearch', ['$window', function($window) {
	return {
		require: 'form',
		restrict: 'AC',
		controller: ['$scope', '$location', '$timeout', function($scope, $location, $timeout) {
			var self = this;

			// handle autocomplete
			$scope.autocomplete = function() {
				var config, acPromise = null;
				if ($scope.searchQuery.length < 3) {
					config = null;
					$location.search({});
				} else {
					config = {
						params: {
							ac: $scope.searchQuery
						}
					};
					$scope.property_filters = [];
					$location.search(config.params);
				}
				// delay the execution of reloading products
				if (acPromise) {
					console.log(self);
					$timeout.cancel(acPromise);
					acPromise = null;
				}
				acPromise = $timeout(function() {
					$scope.$emit('shopCatalogSearch', config);
				}, 500);
			};

			// handle classic search submission.
			$scope.submitSearch = function() {
				if ($scope.searchQuery.length > 1/* && TODO: compare against previous search query */) {
					self.submit();
				}
			};

		}],
		link: function(scope, element, attrs, formController) {
			var i, splitted, queries;
			formController.submit = element[0].submit;

			// convert query string to object
			scope.searchQuery = '';
			queries = $window.location.search.replace(/^\?/, '').split('&');
			for (i = 0; i < queries.length; i++) {
				splitted = queries[i].split('=');
				if (splitted[0] === 'q') {
					scope.searchQuery = decodeURIComponent(splitted[1].split('+').join('%20'));
				}
			}
		}
	};
}]);

})();
