(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.cart', []);

djangoShopModule.controller('CartController', ['$scope', '$http', 'djangoUrl', function($scope, $http, djangoUrl) {
	var cartListURL = djangoUrl.reverse('shop-api:cart-list');
	var isLoading = false;

	this.loadCart = function() {
		$http.get(cartListURL).success(function(cart) {
			console.log('loaded cart: ');
			console.log(cart);
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
			console.log(response);
			return $http.get(cartListURL);
		}).then(function(response) {
			console.log(response);
			angular.copy(response.data, $scope.cart);
		}, function(error) {
			console.error(error);
		}, function() {
			isLoading = false;
		});
	}

	$scope.updateCartItem = function(cart_item) {
		postCartItem(cart_item, 'PUT');
	}

	$scope.deleteCartItem = function(cart_item) {
		postCartItem(cart_item, 'DELETE');
	}

	$scope.watchCartItem = function(cart_item) {
		cart_item.quantity = 0;
		postCartItem(cart_item, 'PUT');
	}
}]);


// Directive <shop-cart>
// handle a djangoSHOP's cart
djangoShopModule.directive('shopCart', function() {
	return {
		restrict: 'EA',
		templateUrl: 'shop/cart.html',
		controller: 'CartController',
		link: function(scope, element, attrs, cartCtrl) {
			cartCtrl.loadCart();
		}
	};
});

// Directive <shop-cart-item>
// handle a djangoSHOP's cart item
djangoShopModule.directive('shopCartItem', function() {
	return {
		require: '^shopCart',
		restrict: 'EA',
		templateUrl: 'shop/cart-item.html',
		controller: 'CartController'
		/*
		scope: {
			cart_item: '=cart_item'
		}
		*/
	};
});

})(window.angular);
