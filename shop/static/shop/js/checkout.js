(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.checkout', []);

// Directive <shop-checkout>
// handle a djangoSHOP's cart
djangoShopModule.directive('shopCheckoutSummary', ['$http', 'djangoUrl', function($http, djangoUrl) {
	var cartListURL = djangoUrl.reverse('shop-api:checkout-summary');
	var scope, isLoading = false;

	function loadCheckout() {
		$http.get(cartListURL).success(function(cart) {
			console.log('loaded cart: ');
			console.log(cart);
			scope.cart = cart;
		}).error(function(msg) {
			console.error("Unable to fetch shopping cart: " + msg);
		});
	}

	return {
		restrict: 'EA',
		link: function($scope, element, attrs) {
			scope = $scope;
			loadCheckout();
		}
	};
}]);



djangoShopModule.directive('shopCheckoutForms', ['$http', 'djangoUrl', 'djangoForm', function($http, djangoUrl, djangoForm) {
	var checkoutFormsURL = djangoUrl.reverse('shop-api:checkout-address-form-submit');
	var scope, isLoading = false;

	function fetchForms() {
		$http.get(checkoutFormsURL).success(function(cart) {
			scope.cart = cart;
		}).error(function(msg) {
			console.error("Unable to fetch checkout forms: " + msg);
		});
	}

	return {
		restrict: 'EA',
		link: function($scope, element, attrs, controller) {
			scope = $scope;
		}
	};
}]);

djangoShopModule.directive('shopCheckoutButton', ['$http', 'djangoUrl', 'djangoForm', function($http, djangoUrl, djangoForm) {
	var checkoutURL = djangoUrl.reverse('shop-api:checkout-submit');
	var element, scope, isLoading = false;

	function submit() {
		$http.post(checkoutURL, scope.data).success(function(response) {
			angular.forEach(response.errors, function(errors, key) {
				djangoForm.setErrors(scope[key], errors);
			});
			// djangoForm.setErrors(scope.shipping_addr_form, response.errors.shipping_addr_form);
		}).error(function(msg) {
			console.error("Unable to submit checkout forms: " + msg);
		});
	}

	function destroy() {
		console.error("Destroy button");
		element.off('click');
	}

	return {
		restrict: 'EA',
		link: function($scope, $element, attrs, controller) {
			scope = $scope;
			element = $element;
			element.on('$destroy', destroy);
			element.on('click', submit);
		}
	};
}]);

})(window.angular);
