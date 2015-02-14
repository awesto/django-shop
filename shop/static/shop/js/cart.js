(function(angular, undefined) {
'use strict';

// module: django.shop
var djangoShopModule = angular.module('django.shop', []);

djangoShopModule.controller('CartController', ['$scope', '$http', 'shopConfig', function($scope, $http, shopConfig) {
	var self = this;

	self.loadCart = function() {
		$http.get(shopConfig.cartListURL).success(function(cart) {
			console.log('loaded cart: ');
			console.log(cart);
			$scope.cart = cart;
		}).error(function(msg) {
			console.error('Unable to fetch shopping cart: ' + msg);
		});
	}
}]);

// This directive handles a djangoSHOP's cart
djangoShopModule.directive('shopCart', function() {
	return {
		restrict: 'EA',
		templateUrl: 'template/shop/cart.html',
		controller: 'CartController',
		link: function(scope, element, attrs, cartCtrl) {
			cartCtrl.loadCart();
		}
	};
});

djangoShopModule.directive('shopCartItem', function() {
	return {
		require: '^shopCart',
		restrict: 'EA',
		templateUrl: 'template/shop/cart-item.html'
	};
});

})(window.angular);
