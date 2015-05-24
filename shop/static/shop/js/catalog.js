(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.product', ['ui.bootstrap']);


// Infinite scroll directive <ANY shop-scroll-spy="loadMore()">
// Add this directive to a DOM element, wrapping the list views.
// Whenever the client scrolls the browser window beyond the current height of the wrapping element,
// the function `loadMore()` from the lists controller is invoked. This function then shall load
// more elements to the list view and thus increase the height of the DOM element.
djangoShopModule.directive('shopScrollSpy', ['$document', function($document) {
	return function(scope, element, attrs) {
		var body = $document.find('body')[0], docElem = $document[0].documentElement, spyElem = element[0],
			offsetBottom = angular.isNumber(attrs.shopOffsetBottom) ? parseInt(attrs.shopOffsetBottom) : 0;

		$document.on('scroll', function(evt) {
			console.log(body.scrollTop + docElem.clientHeight);
			console.log(spyElem.offsetTop + spyElem.clientHeight + offsetBottom);
			if (Math.ceil(body.scrollTop + docElem.clientHeight) >= Math.floor(spyElem.offsetTop + spyElem.clientHeight + offsetBottom)) {
				scope.$apply(attrs.shopScrollSpy);
			}
		});
	};
}]);


djangoShopModule.controller('AddToCartCtrl', ['$scope', '$http', '$window', '$modal',
                                               function($scope, $http, $window, $modal) {
	var updateUrl = $window.location.pathname + '/add-to-cart' + $window.location.search;
	var isLoading = false;
	var prevContext = null;

	this.loadContext = function() {
		$http.get(updateUrl).success(function(context) {
			console.log('loaded product:');
			console.log(context);
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

	$scope.addToCart = function(cart_url) {
		$modal.open({
			templateUrl: 'AddToCartModalDialog.html',
			controller: 'ModalInstanceCtrl',
			resolve: {
				modal_context: function() {
					return {cart_url: cart_url, context: $scope.context};
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
