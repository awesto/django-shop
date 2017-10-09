(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.method-form', ['djng']);


module.directive('shopPaymentMethod', ['$timeout', function($timeout) {
	return {
		restrict: 'A',
		require: 'djngEndpoint',
		link: function(scope, element, attrs, controller) {
			var ready = false;

			$timeout(function() {
				// delay until first digest cycle
				ready = true;
			});

			scope.updatePaymentMethod = function() {
				if (ready)
					return controller.uploadScope('PUT').then(function() {
						scope.$emit('shop.checkout.digest');
					});
			};
		}
	};
}]);


module.directive('shopShippingMethod', ['$timeout', function($timeout) {
	return {
		restrict: 'A',
		require: 'djngEndpoint',
		link: function(scope, element, attrs, controller) {
			var ready = false;

			$timeout(function() {
				// delay until first digest cycle
				ready = true;
			});

			scope.updateShippingMethod = function() {
				if (ready)
					return controller.uploadScope('PUT').then(function() {
						scope.$emit('shop.checkout.digest');
					})
			};
		}
	};
}]);


})(window.angular);
