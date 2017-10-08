(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.address', ['djng']);

var dialogFormDirective = ['$timeout', function($timeout) {
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

			scope.switchSiblingAddress = function() {
				if (endpointController && modelController)
					return endpointController.uploadScope('GET', {priority: modelController.$modelValue});
			};

			scope.deleteSiblingAddress = function(priority) {
				if (endpointController)
					return endpointController.uploadScope('DELETE', {priority: priority});
			};

			scope.updateSiblingAddress = function(priority) {
				if (endpointController)
					return endpointController.uploadScope('PUT', {priority: priority});
			};
		}
	};
}];

module.directive('select', dialogFormDirective);
module.directive('button', dialogFormDirective);


})(window.angular);
