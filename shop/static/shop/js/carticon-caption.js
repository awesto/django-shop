(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.carticon_caption', ['djng.urls']);

// Directive <ANY shop-carticon-caption caption-data="{num_items: 7}">
// Use this directive to handle the caption often displayed near a cart item. This caption
// can for instance show the number of items in the cart, the total quantity of all items, the
// final total of the cart, or whatever the merchant desires.
// Whenever this directive receives an event of type `shopUpdateCarticonCaption`, then it updates
// the cart-icon caption with the current state of the cart. The emitter of that event may pass in
// the new caption object itself, otherwise this directive will fetch that data from the server.
djangoShopModule.directive('shopCarticonCaption', ['$rootScope', '$http', 'djangoUrl', function($rootScope, $http, djangoUrl) {
	var updateCaptionURL = djangoUrl.reverse('shop:cart-update-caption');

	return {
		templateUrl: 'shop/carticon-caption.html',
		link: function(scope, element, attrs) {
			function updateCarticonCaption() {
				$http.get(updateCaptionURL).success(function(caption) {
					angular.extend(scope.caption, caption);
				}).error(function(msg) {
					console.error("Unable to fetch caption for cart icon: " + msg);
				});
			}

			scope.caption = scope.$eval(attrs.captionData);

			// listen on events of type `shopUpdateCarticonCaption`
			$rootScope.$on('shopUpdateCarticonCaption', function(event, caption) {
				if (angular.isObject(caption)) {
					// the updated carticon's caption is passed in by the emitter
					angular.extend(scope.caption, caption);
				} else {
					// otherwise update the carticon's caption fetching the server
					updateCarticonCaption();
				}
			});
		}
	};
}]);

})(window.angular);
