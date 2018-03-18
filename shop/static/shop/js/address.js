(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.address', ['djng.forms']);

module.directive('shopAddressForm', ['$timeout', function($timeout) {
	return {
		restrict: 'A',
		require: ['form', 'djngEndpoint'],
		scope: true,
		link: function(scope, element, attrs, controllers) {
			var formController = controllers[0], endpointController = controllers[1], ready = false, watchers = [];

			scope.switchSiblingAddress = function(activePriority) {
				if (ready) {
					endpointController.uploadScope('GET', {priority: activePriority}).then(function(request) {
						formController.$setPristine();
					});
				}
			};

			scope.deleteSiblingAddress = function() {
				return endpointController.uploadScope('DELETE', {priority: formController.active_priority.$modelValue});
			};

			scope.updateSiblingAddress = function() {
				if (ready && formController.$valid)
					return endpointController.uploadScope('PUT', {priority: formController.active_priority.$modelValue});
			};

			function validateForm() {
				formController.$valid = formController.$valid || formController.use_primary_address.$modelValue;
				formController.$invalid = !formController.$valid;
			}

			$timeout(function() {
				// delay until first digest cycle
				ready = true;
			});
			if (formController.hasOwnProperty('use_primary_address')) {
				watchers.push(scope.$watch(attrs.name + '.$valid', validateForm));
				watchers.push(scope.$watch(attrs.name + '.use_primary_address.$modelValue', validateForm));
			}

			scope.$on('$destroy', function() {
				angular.forEach(watchers, watcher);
			});
		}
	}
}]);


})(window.angular);
