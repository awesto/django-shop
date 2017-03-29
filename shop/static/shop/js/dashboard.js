(function(angular, undefined) {
'use strict';

var djangoShopDashboard = angular.module('djangoShopDashboard');

// Use directive <ANY shop-dashboard-list> to render the list views for various models on the
// dashboard's list views.
djangoShopDashboard.directive('shopDashboardList', ['$window', function($window) {
	return {
		restrict: 'EAC',
		controller: ['$scope', '$http', '$sce', function($scope, $http, $sce) {
			$scope.results = [];

			this.load = function(config) {
				$scope.isLoading = true;
				config.method = 'GET';
				$http(config).success(function(response) {
					config.url = response.next;
					angular.forEach(response.results, function(entry) {
						for (var property in entry) {
							if (entry.hasOwnProperty(property) && angular.isString(entry[property])) {
								entry[property] = $sce.trustAsHtml(entry[property]);
							}
						}
					});
					$scope.results = $scope.results.concat(response.results);
					$scope.isLoading = false;
				}).error(function() {
					$scope.isLoading = false;
				});
			};

		}],
		link: function(scope, element, attrs, controller) {
			var config = {url: attrs.shopDashboardList};

			scope.loadMore = function() {
				console.log('loadMore');
				if (config.url) {
					controller.load(config);
				}
			};
		}
	};
}]);


})(window.angular);
