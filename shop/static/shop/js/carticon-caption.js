(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.carticon_caption', []);

// Directive <shop-carticon-caption endpoint="{% url 'shop:cart-fetch-caption' %}" initial-caption="{num_items: 7}">
// Use this directive to handle the caption, often displayed near by the cart item symbol.
// This caption can for instance show the number of items in the cart, the total quantity of all items,
// the final total of the cart, or whatever the merchant desires. Override the `CartIconCaptionSerializer`
// to add alternative fields.
// Whenever this directive receives an event of type `shop.carticon.caption`, then it updates
// the cart-icon's caption with an actual state of the cart. The emitter of that event may pass
// the new caption object itself, otherwise this directive will fetch the caption data from the server.
djangoShopModule.directive('shopCarticonCaption', ['$http', '$timeout', function($http, $timeout) {
	return {
		restrict: 'E',
		templateUrl: 'shop/carticon-caption.html',
		scope: true,
		link: function(scope, element, attrs) {
			if (!angular.isString(attrs.endpoint))
				throw new Error("The directive <shop-carticon-caption ...> must specify an endpoint.")

			scope.caption = scope.$eval(attrs.initialCaption);
			if (!scope.caption) {
				scope.caption = {};
				$timeout(fetchCaption);
			}

			function fetchCaption() {
				$http.get(attrs.endpoint).then(function(response) {
					angular.extend(scope.caption, response.data);
				});
			}

			// listen on events named `shop.carticon.caption`
			scope.$on('shop.carticon.caption', function(event, caption) {
				if (angular.isObject(caption)) {
					// the updated carticon's caption is passed in by the emitter
					angular.extend(scope.caption, caption);
				} else {
					// otherwise update the carticon's caption fetching the server
					fetchCaption();
				}
			});
		}
	};
}]);

})(window.angular);
