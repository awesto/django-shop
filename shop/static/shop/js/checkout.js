(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.checkout', []);


// Directive <form shop-checkout-form> (must be an attribute of the <form> element)
// handle checkout updates
djangoShopModule.directive('shopCheckoutForm', ['$http', 'djangoUrl', 'djangoForm', function($http, djangoUrl, djangoForm) {
	var updateURL = djangoUrl.reverse('shop-api:checkout-update');
	var $scope, isLoading = false;

	function update() {
		if (isLoading)
			return;
		isLoading = true;
		$http.post(updateURL, $scope.data).success(function(response) {
			delete response.errors;
			$scope.cart = response;
		}).error(function(msg) {
			console.error("Unable to update checkout forms: " + msg);
		}).finally(function() {
			isLoading = false;
		});
	}

	return {
		restrict: 'A',
		require: 'form',
		link: function(scope, element, attrs) {
			$scope = scope;
			$scope.update = update;
		}
	};
}]);


djangoShopModule.directive('shopCheckoutButton', ['$http', 'djangoUrl', 'djangoForm', function($http, djangoUrl, djangoForm) {
	var checkoutUpdateURL = djangoUrl.reverse('shop-api:checkout-update');
	var element, scope, isLoading = false;

	function purchase() {
		$http.post(checkoutUpdateURL, scope.data).success(function(response) {
			angular.forEach(response.errors, function(errors, key) {
				djangoForm.setErrors(scope[key], errors);
			});
			delete response.errors;
			scope.cart = response;
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
			element.on('click', purchase);
		}
	};
}]);

})(window.angular);
