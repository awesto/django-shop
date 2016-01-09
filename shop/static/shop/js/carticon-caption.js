(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.carticon_caption', ['ng.django.urls']);

// Directive <ANY shop-cart-count-items>{{ count_items }}</ANY>
// To be used for updating the number of items in the cart whenever
// this directive receives an event of type ``.
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

			scope.caption = {num_items: attrs.numItems, total_quantity: attrs.totalQuantity};

			// listen on events of type `shopUpdatedCartLegend`
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
