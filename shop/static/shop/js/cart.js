(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.cart', []);


djangoShopModule.controller('cartController',
                            ['$http', '$q', '$rootScope', '$scope',
                            function($http, $q, $rootScope, $scope) {
	var self = this;

	this.loadCart = function() {
		var deferred = $q.defer();
		$http.get(self.endpoint).then(function(response) {
			$scope.cart = response.data;
			deferred.resolve(response);
		});
		return deferred.promise;
	};
}]);


// Directive <ANY shop-cart="endpoint">
// Handle a django-SHOP's cart by using "{% url 'shop:cart-list' %}" as endpoint.
// Handle the watch-list by using "{% url 'shop:watch-list' %}" as endpoint.
djangoShopModule.directive('shopCart', function() {
	return {
		restrict: 'A',
		scope: true,
		transclude: true,
		controller: 'cartController',
		link: function(scope, element, attrs, controller, transclude) {
			if (!attrs.shopCart)
				throw new Error('The directive <ANY shop-cart="..."> must specify an endpoint.');
			controller.endpoint = attrs.shopCart;
			transclude(scope, function(clone) {
				element.append(clone);
			});
			controller.loadCart();
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
		controller: ['$http', '$q', '$rootScope', '$scope', function($http, $q, $rootScope, $scope) {
			function uploadCartItem(method, cartItem) {
				var deferred = $q.defer();
				$http({
					url: cartItem.url,
					method: method,
					data: cartItem
				}).then(function(response) {
					$rootScope.$broadcast('shop.cart.change', response.data.cart);
					$rootScope.$broadcast('shop.messages.fetch');
					deferred.resolve(response);
				});
				return deferred.promise;
			}

			function refreshCart(cart) {
				$scope.cart.extra_rows = cart.extra_rows;
				$scope.cart.total_quantity = cart.total_quantity;
				$scope.cart.num_items = cart.num_items;
				$scope.cart.subtotal = cart.subtotal;
				$scope.cart.total = cart.total;
			}

			// change quantity of item in the cart
			$scope.updateCartItem = function(cartItem) {
				uploadCartItem('PUT', cartItem).then(function(response) {
					angular.extend($scope.cart_item, response.data.cart_item);
					refreshCart(response.data.cart);
				});
			};

			// delete an item from the cart
			$scope.deleteCartItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				uploadCartItem('DELETE', cartItem).then(function(response) {
					if (index !== -1) {
						$scope.cart.items.splice(index, 1);
					}
					refreshCart(response.data.cart);
				});
			};

			// put a cart item into the watch-list
			$scope.watchCartItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				cartItem.quantity = 0;
				uploadCartItem('PUT', cartItem).then(function(response) {
					if (index !== -1) {
						$scope.cart.items.splice(index, 1);
					}
					refreshCart(response.data.cart);
				});
			};

			// re-add a watched item to the cart
			$scope.addWatchItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				uploadCartItem('PUT', cartItem).then(function() {
					if (index !== -1) {
						$scope.cart.items.splice(index, 1);
					}
				});
			};

			// delete an item from the watch-list
			$scope.deleteWatchItem = function(cartItem) {
				var index = $scope.cart.items.indexOf(cartItem);
				uploadCartItem('DELETE', cartItem).then(function() {
					if (index !== -1) {
						$scope.cart.items.splice(index, 1);
					}
				});
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
		scope: true,
		controller: 'cartController',
		link: function(scope, element, attrs, controller) {
			var timer = null;
			if (!attrs.shopDropdownCart)
				throw new Error('The directive <ANY shop-dropdown-cart="..."> must specify an endpoint.');
			controller.endpoint = attrs.shopDropdownCart;

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

			element.on('mouseenter', function() {
				scope.dropdownOpen = true;
				scope.$apply();
			});
			element.on('mouseleave', triggerDropdown);
			$rootScope.$on('shop.cart.change', function(event, cart) {
				if (angular.isObject(cart)) {
					scope.cart = cart;
					triggerDropdown();
				} else {
					controller.loadCart().then(triggerDropdown);
				}
			});

			try {
				// try with pre-rendered cart content
				scope.cart = JSON.parse(document.getElementById(attrs.shopDropdownCart).text);
			} catch (e) {
				// otherwise load cart content from endpoint
				controller.loadCart();
			}
		}
	}
}]);


})(window.angular);
