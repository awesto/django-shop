(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.cart_icon', ['ng.django.urls']);

// Directive <ANY shop-cart-count-items>{{ count_items }}</ANY>
// To be used for updating the number of items in the cart whenever
// this directive receives an event of type ``.
djangoShopModule.directive('shopCartCountItems', ['$rootScope', '$compile', '$http', 'djangoUrl', function($rootScope, $compile, $http, djangoUrl) {
	var cartCountItemsURL = djangoUrl.reverse('shop:cart-count-items');

	return {
		link: function(scope, element, attrs) {
			var template = element.clone().removeAttr('shop-cart-count-items');
			element.replaceWith($compile(template)(scope));

			function fetchCountItems() {
				$http.get(cartCountItemsURL).success(function(data) {
					scope.count_items = data.count_items;
				}).error(function(msg) {
					console.error('Unable to fetch shopping cart: ' + msg);
				});
			}

			if (parseInt(attrs.shopCartCountItems) >= 0) {
				scope.count_items = attrs.shopCartCountItems;
			} else {
				fetchCountItems();
			}

			// listen on events of type `shopUpdatedCartItems`
			$rootScope.$on('shopUpdatedCartItems', function(event, count_cart_items) {
				if (angular.isNumber(count_cart_items)) {
					scope.count_items = count_cart_items;
				} else {
					// otherwise fetch the current number of cart items from the server
					fetchCountItems();
				}
			});
		}
	};
}]);

})(window.angular);
