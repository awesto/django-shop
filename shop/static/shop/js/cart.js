(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.cart', ['djng.urls']);


// Directive <shop-cart endpoint="/path/to/cart/endpoint">
// Handle a django-SHOP's cart. Directive <shop-cart watch="watch"> renders the cart as watch-list.
djangoShopModule.directive('shopCart', function() {
	return {
		restrict: 'EA',
		templateUrl: 'shop/cart.html',
		controller: ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {
			var self = this, isLoading = false;

			this.loadCart = function() {
				if (isLoading)
					return;
				isLoading = true;
				$http.get(self.endpoint).then(function(response) {
					$scope.cart = response.data;
				}).finally(function() {
					isLoading = false;
				});
			};

			$rootScope.$on('shop.checkout.digest', this.loadCart);
		}],
		link: {
			pre: function(scope, element, attrs, controller) {
				controller.endpoint = attrs.endpoint;
			},
			post: function(scope, element, attrs, controller) {
				controller.loadCart();
			}
		}
	};
});


// Directive <shop-cart-item>
// handle a django-SHOP's cart item
djangoShopModule.directive('shopCartItem', function() {
	return {
		require: '^shopCart',
		restrict: 'EA',
		templateUrl: 'shop/cart-item.html',
		controller: ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {
			var isLoading = false;

			function uploadCartItem(method, cartItem) {
				if (isLoading)
					return;
				isLoading = true;
				$http({
					url: cartItem.url,
					method: method,
					data: cartItem
				}).then(function(response) {
					angular.extend($scope.cart_item, response.data.cart_item);
					angular.extend($scope.cart, response.data.cart);
					$rootScope.$broadcast('shop.carticon.caption');
				}).finally(function() {
					isLoading = false;
				});
			}

			$scope.updateCartItem = function(cartItem) {
				uploadCartItem('PUT', cartItem);
			};

			$scope.deleteCartItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				uploadCartItem('DELETE', cartItem);
				if (index !== -1) {
					$scope.cart.items.splice(index, 1);
				}
			};

			// put a cart item into the watch list
			$scope.watchCartItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				cartItem.quantity = 0;
				uploadCartItem('PUT', cartItem);
				if (index !== -1) {
					$scope.cart.items.splice(index, 1);
				}
			};

			// readd a cart item from the watch list to the cart
			$scope.addCartItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				uploadCartItem('PUT', cartItem);
				if (index !== -1) {
					$scope.cart.items.splice(index, 1);
				}
			};
		}]
	};
});

})(window.angular);
