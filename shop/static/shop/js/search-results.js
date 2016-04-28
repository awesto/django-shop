(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.searchResults', []);

// Directive <ANY shop-search-results> used for controlling the search result list.
// The initial data to this directive must be provided using the searchResultsProvider
// during the configuration of the application.
djangoShopModule.directive('shopSearchResults', ['$http', function($http) {
	return {
		restrict: 'EAC',
		controller: ['$scope', 'searchResults', function($scope, searchResults) {
			$scope.search_data = searchResults.search_data;
			$scope.isLoading = false;

			$scope.loadMore = function() {
				if ($scope.isLoading || !$scope.search_data.next)
					return;
				console.log('load more search results ...');
				$scope.isLoading = true;
				$http.get($scope.search_data.next).success(function(response) {
					$scope.search_data.next = response.next;
					$scope.search_data.count = response.count;
					$scope.search_data.results = $scope.search_data.results.concat(response.results);
					$scope.isLoading = false;
				}).error(function() {
					$scope.search_data.next = null;
					$scope.isLoading = false;
				});
			};
		}]
	};
}]);

djangoShopModule.provider('searchResults', function() {
	var self = this;

	this.setSearchResults = function(search_data) {
		self.search_data = search_data;
	};

	this.$get = function() {
		return self;
	};
});

})(window.angular);
