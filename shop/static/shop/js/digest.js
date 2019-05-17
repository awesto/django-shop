(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.digest', []);


djangoShopModule.provider('checkoutDigest', function() {
	var isDirty = false, initialDigest = {}, endpointURL;

	this.setEndpoint = function(url) {
		endpointURL = url;
	};

	this.setInitialTag = function(initialTag) {
		if (angular.isObject(initialTag)) {
			angular.extend(initialDigest, initialTag);
		} else {
			isDirty = true;
		}
	};

	this.$get = ['$http', '$rootScope', '$timeout', function($http, $rootScope, $timeout) {
		// register the listener once for all directives of this page
		$rootScope.checkoutDigest = {};
		$rootScope.$on('shop.checkout.digest', fetchCheckoutDigest);
		$timeout(function() {
			if (isDirty) {
				fetchCheckoutDigest();
			} else {
				angular.extend($rootScope.checkoutDigest, initialDigest);
			}
		});

		function fetchCheckoutDigest() {
			$http.get(endpointURL).then(function(response) {
				$rootScope.cart = angular.isObject($rootScope.cart) ? $rootScope.cart : {};
				angular.extend($rootScope.cart, response.data.cart_summary);
				angular.extend($rootScope.checkoutDigest, response.data.checkout_digest);
			});
		}

		return this;
	}];
});


// Use the directive <shop-checkout-digest initial-tag="{extra_annotation: 'wait til Monday'}">
// as a wrapper around all checkout forms and the cart summary. It enriches the scope with objects
// `cart` and `checkout_digest`. They contain the current state of the cart and the checkout
// digest tags.
djangoShopModule.directive('shopCheckoutDigest', ['checkoutDigest', function(checkoutDigest) {
	return {
		restrict: 'E',
		scope: true,
		link: function(scope, element, attrs) {
			checkoutDigest.setInitialTag(scope.$eval(attrs.initialTag));
		}
	};
}]);

})(window.angular);
