(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.digest', []);


// Use the directive <ANY shop-checkout-digest="path/to/endpoint"> as a wrapper around all checkout
// forms and the cart summary. It enriches the scope with objects `cart` and
// `checkout_digest`. They contain the current state of the cart and the checkout
// digest tags.
module.directive('shopCheckoutDigest', ['$http', '$rootScope', function($http, $rootScope) {
	return {
		restrict: 'EA',
		link: function(scope, element, attrs) {
			var endpoint = attrs.shopCheckoutDigest;
			if (!angular.isString(endpoint))
				throw new Error("The directive 'shop-checkout-digest' must specify an endpoint.")

			if (!$rootScope.$$listeners['shop.checkout.digest']) {
				$rootScope.$on('shop.checkout.digest', function() {
					$http.get(endpoint).then(function(response) {
						angular.extend($rootScope, response.data);
					});
				});
			}
		}
	};
}]);

})(window.angular);
