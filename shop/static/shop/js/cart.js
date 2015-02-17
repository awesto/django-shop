(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop', []);

djangoShopModule.controller('CartController', ['$scope', '$http', 'shopConfig', function($scope, $http, shopConfig) {
	this.loadCart = function() {
		$http.get(shopConfig.cartListURL).success(function(cart) {
			console.log('loaded cart: ');
			console.log(cart);
			$scope.cart = cart;
		}).error(function(msg) {
			console.error('Unable to fetch shopping cart: ' + msg);
		});
	}

	function postCartItem(cart_item, method) {
		console.log(cart_item);
		var config = {headers: {'X-HTTP-Method-Override': method}};
		$http.post(cart_item.url, cart_item, config).then(function(response) {
			console.log(response);
			return $http.get(shopConfig.cartListURL/* + '?digest'*/);
		}).then(function(response) {
			console.log(response);
			angular.copy(response.data, $scope.cart);
		}, function(error) {
			console.error(error);
		});
	}

	$scope.updateCartItem = function(cart_item) {
		postCartItem(cart_item, 'PUT');
	}

	$scope.deleteCartItem = function(cart_item) {
		postCartItem(cart_item, 'DELETE');
	}
}]);

// Directive <shop-cart>
// handle a djangoSHOP's cart
djangoShopModule.directive('shopCart', function(shopConfig) {
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
djangoShopModule.directive('shopCartItem', function(shopConfig) {
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
