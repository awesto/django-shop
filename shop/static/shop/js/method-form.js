(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.method-form', ['djng']);

module.directive('input', ['$timeout', function($timeout) {
	return {
		restrict: 'E',
		require: ['^?djngEndpoint', '?ngModel'],
		link: function(scope, element, attrs, controllers) {
			var endpointController, modelController;
			if (!controllers[0])
				return;

			$timeout(function() {
				// delay until first digest cycle
				endpointController = controllers[0];
				modelController = controllers[1];
			});

			scope.updateMethodForm = function() {
				if (endpointController)
					return endpointController.uploadScope('PUT');
			};
		}
	};
}]);

})(window.angular);
