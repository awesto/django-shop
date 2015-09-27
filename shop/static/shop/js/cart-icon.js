(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.cart', ['ng.django.urls']);

// Directive <ANY shop-cart-count-items>{{ count_items }}</ANY>
// To be used for updating the number of items in the cart whenever
// this directive receives an event of type ``.
djangoShopModule.directive('shopCartCountItems', ['$rootScope', '$http', 'djangoUrl', function($rootScope, $http, djangoUrl) {
	var cartCountItemsURL = djangoUrl.reverse('shop:cart-count-items');

	return {
		link: function(scope, element, attrs) {
			function fetchCountItems() {
				$http.get(cartCountItemsURL).success(function(data) {
					element.html(data.count_items);
				}).error(function(msg) {
					console.error('Unable to fetch shopping cart: ' + msg);
				});
			}

			if (!parseInt(element.html())) {
				fetchCountItems();
			}

			// listen on events of type `shopUpdatedCartItems`
			$rootScope.$on('shopUpdatedCartItems', function(event, count_cart_items) {
				if (angular.isNumber(count_cart_items)) {
					element.html(count_cart_items);
				} else {
					// otherwise fetch the current number of cart items from the server
					fetchCountItems();
				}
			});
		}
	};
}]);

})(window.angular);
