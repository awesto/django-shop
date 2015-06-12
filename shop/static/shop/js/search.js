(function() {
'use strict';

//module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.search', []);

// Directive <form shop-product-search ...>
djangoShopModule.directive('shopProductSearch', ['$window', function($window) {
	return {
		require: 'form',
		restrict: 'AC',
		controller: ['$scope', function($scope) {
			// shall be overridden by child controller
			$scope.autocomplete = function() {};
		}],
		link: function(scope, element, attrs, formController) {
			var i, search = {}, split, queries;

			// convert query string to object
			queries = $window.location.search.replace(/^\?/, '').split('&');
			for (i = 0; i < queries.length; i++) {
				split = queries[i].split('=');
				search[split[0]] = split[1];
			}
			scope.searchQuery = search['q'] || '';

			scope.submit = function() {
				if (scope.searchQuery.length > 1 && scope.searchQuery !== search['q']) {
					element[0].submit();
				}
			}
		}
	};
}]);

})();
