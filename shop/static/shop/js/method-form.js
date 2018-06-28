(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.method-form', ['djng.forms']);


module.directive('shopMethodForm', ['$timeout', function($timeout) {
	return {
		restrict: 'A',
		require: 'djngEndpoint',
		scope: true,
		link: function(scope, element, attrs, controller) {
			var ready = false;

			$timeout(function() {
				// delay until first digest cycle
				ready = true;
			});

			scope.updateMethod = function() {
				if (ready) {
					controller.uploadScope('PUT').then(function() {
						scope.$emit('shop.checkout.digest');
					});
				}
			};
		}
	};
}]);


})(window.angular);
