(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.cart', ['djng.urls']);

djangoShopModule.controller('CartController', ['$scope', '$http', function($scope, $http) {
	var isLoading = false;

	this.loadCart = function() {
		$http.get($scope.cartListURL).success(function(cart) {
			$scope.cart = cart;
		}).error(function(msg) {
			console.error('Unable to fetch shopping cart: ' + msg);
		});
	}

	function postCartItem(cart_item, method) {
		var config = {headers: {'X-HTTP-Method-Override': method}};
		if (isLoading)
			return;
		isLoading = true;
		$http.post(cart_item.url, cart_item, config).then(function(response) {
			return $http.get($scope.$parent.cartListURL);
		}).then(function(response) {
			isLoading = false;
			angular.copy(response.data, $scope.cart);
			$scope.$emit('shopUpdateCarticonCaption', response.data);
		}, function(error) {
			isLoading = false;
			console.error(error);
		});
	}

	$scope.updateCartItem = function(cart_item) {
		postCartItem(cart_item, 'PUT');
	}

	$scope.deleteCartItem = function(cart_item) {
		postCartItem(cart_item, 'DELETE');
	}

	// put a cart item into the watch list
	$scope.watchCartItem = function(cart_item) {
		cart_item.quantity = 0;
		postCartItem(cart_item, 'PUT');
	}

	// readd a cart item from the watch list to the cart
	$scope.addCartItem = function(cart_item) {
		postCartItem(cart_item, 'PUT');
	}
}]);


// Directive <shop-cart>
// Handle a django-SHOP's cart. Directive <shop-cart watch="watch"> renders the cart as watch-list.
djangoShopModule.directive('shopCart', ['djangoUrl', function(djangoUrl) {
	var cartListURL = djangoUrl.reverse('shop:cart-list');
	var watchListURL = djangoUrl.reverse('shop:watch-list');
	return {
		restrict: 'EA',
		templateUrl: 'shop/cart.html',
		controller: 'CartController',
		link: {
			pre: function(scope, element, attrs) {
				scope.cartListURL = attrs.watch === 'watch' ? watchListURL : cartListURL;
			},
			post: function(scope, element, attrs, cartCtrl) {
				cartCtrl.loadCart();
			}
		}
	};
}]);


// Directive <shop-cart-item>
// handle a django-SHOP's cart item
djangoShopModule.directive('shopCartItem', function() {
	return {
		require: '^shopCart',
		restrict: 'EA',
		templateUrl: 'shop/cart-item.html',
		controller: 'CartController'
	};
});

})(window.angular);
