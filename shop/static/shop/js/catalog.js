(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.catalog', ['ui.bootstrap']);

djangoShopModule.controller('AddToCartCtrl', ['$scope', '$http', '$window', '$modal',
                                               function($scope, $http, $window, $modal) {
	var updateUrl = $window.location.pathname + '/add-to-cart/' + $window.location.search;
	var isLoading = false;
	var prevContext = null;

	this.loadContext = function() {
		$http.get(updateUrl).success(function(context) {
			prevContext = context;
			$scope.context = angular.copy(context);
		}).error(function(msg) {
			console.error('Unable to get context: ' + msg);
		});
	};

	$scope.updateContext = function() {
		if (isLoading || angular.equals($scope.context, prevContext))
			return;
		isLoading = true;
		$http.post(updateUrl, $scope.context).success(function(context) {
			console.log('loaded product:');
			console.log(context);
			prevContext = context;
			$scope.context = angular.copy(context);
		}).error(function(msg) {
			console.error('Unable to update context: ' + msg);
		}).finally(function() {
			isLoading = false;
		});
	};

	$scope.addToCart = function(cart_url, extra_context) {
		$modal.open({
			templateUrl: 'AddToCartModalDialog.html',
			controller: 'ModalInstanceCtrl',
			resolve: {
				modal_context: function() {
					return {
						cart_url: cart_url,
						context: angular.extend(angular.isObject(extra_context) ? extra_context : {}, $scope.context)
					};
				}
			}
		}).result.then(function(next_url) {
			$window.location.href = next_url;
		});
	};

}]);

djangoShopModule.controller('ModalInstanceCtrl', ['$scope', '$http', '$modalInstance', 'modal_context',
                                        function($scope, $http, $modalInstance, modal_context) {
	var isLoading = false;
	console.log(modal_context);
	$scope.proceed = function(next_url) {
		if (isLoading)
			return;
		isLoading = true;
		$http.post(modal_context.cart_url, $scope.context).success(function() {
			$modalInstance.close(next_url);
		}).error(function() {
			// TODO: tell us something went wrong
			$modalInstance.dismiss('cancel');
		}).finally(function() {
			isLoading = false;
		});
	};

	$scope.cancel = function () {
		$modalInstance.dismiss('cancel');
	};

	$scope.context = angular.copy(modal_context.context);
}]);


// Directive <shop-add-to-cart>
// handle dialog box on the product's detail page to add a product to the cart
djangoShopModule.directive('shopAddToCart', function() {
	return {
		restrict: 'EAC',
		controller: 'AddToCartCtrl',
		link: function(scope, element, attrs, AddToCartCtrl) {
			AddToCartCtrl.loadContext();
		}
	};
});

})(window.angular);
