(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.cart', []);


// Directive <ANY shop-cart="endpoint">
// Handle a django-SHOP's cart by using "{% url 'shop:cart-list' %}" as endpoint.
// Handle the watch-list by using "{% url 'shop:watch-list' %}" as endpoint.
djangoShopModule.directive('shopCart', function() {
	return {
		restrict: 'A',
		scope: true,
		transclude: true,
		controller: ['$http', '$rootScope', '$scope', function($http, $rootScope, $scope) {
			var self = this;

			this.loadCart = function() {
				if ($scope.isLoading)
					return;
				$scope.isLoading = true;
				$http.get(self.endpoint).then(function(response) {
					$scope.cart = response.data;
				}).finally(function() {
					$scope.isLoading = false;
				});
			};

			$rootScope.$on('shop.cart.change', this.loadCart);
			$rootScope.$on('shop.checkout.digest', this.loadCart);
		}],
		link: function(scope, element, attrs, controller, transclude) {
			if (!attrs.shopCart.startsWith('/'))
				throw new Error('The directive <ANY shop-cart="..."> must specify an endpoint.');
			controller.endpoint = attrs.shopCart;
			transclude(scope, function(clone) {
				element.append(clone);
			});
			try {
				// try with pre-rendered cart content
				scope.cart = JSON.parse(document.getElementById(attrs.shopCart).text);
			} catch (e) {
				// otherwise load cart content from endpoint
				controller.loadCart();
			}
		}
	};
});


// Directive <ANY shop-cart-item>
// handle a django-SHOP's cart item, when using the cart in edit mode.
djangoShopModule.directive('shopCartItem', function() {
	return {
		require: '^shopCart',
		restrict: 'EA',
		transclude: true,
		controller: ['$http', '$rootScope', '$scope', function($http, $rootScope, $scope) {
			var self = this;

			function uploadCartItem(method, cartItem) {
				self.deleteCartItem;
				if ($scope.isLoading)
					return;
				$scope.isLoading = true;
				$http({
					url: cartItem.url,
					method: method,
					data: cartItem
				}).then(function(response) {
					angular.extend($scope.cart_item, response.data.cart_item);
					angular.extend($scope.cart, response.data.cart);
					$rootScope.$broadcast('shop.cart.change');
				}).finally(function() {
					$scope.isLoading = false;
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
		}],
		link: function(scope, element, attrs, controller, transclude) {
			transclude(scope, function(clone, scope) {
				element.append(clone);
			});
		}
	};
});

// Directive <ANY shop-dropdown-cart>
djangoShopModule.directive('shopDropdownCart', ['$rootScope', '$timeout', function($rootScope, $timeout) {
	return {
		restrict: 'A',
		link: function(scope, element) {
			var timer = null;
			function triggerDropdown() {
				scope.dropdownOpen = true;
				if (timer) {
					$timeout.cancel(timer);
					timer = null;
				}
				timer = $timeout(function() {
					scope.dropdownOpen = false;
				}, 3000);
			}

			$rootScope.$on('shop.cart.change', triggerDropdown);
			element.on('mouseenter', function() {
				scope.dropdownOpen = true;
				scope.$apply();
			});
			element.on('mouseleave', triggerDropdown);
		}
	}
}]);

})(window.angular);
