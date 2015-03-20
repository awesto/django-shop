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


djangoShopModule.directive('shopPurchaseButton', ['$http', 'djangoUrl', 'djangoForm', function($http, djangoUrl, djangoForm) {
	var purchaseURL = djangoUrl.reverse('shop-api:checkout-purchase');
	return {
		restrict: 'EA',
		link: function(scope, element, attrs) {
			var isLoading = false;
			element.on('$destroy', function() {
				element.off('click');
			});
			element.on('click', function() {
				$http.post(purchaseURL, scope.data).success(function(response) {
					angular.forEach(response.errors, function(errors, key) {
						djangoForm.setErrors(scope[key], errors);
					});
					delete response.errors;
					scope.cart = response;
				}).error(function(msg) {
					console.error("Unable to submit checkout forms: " + msg);
				});
			});
		}
	};
}]);

})(window.angular);
