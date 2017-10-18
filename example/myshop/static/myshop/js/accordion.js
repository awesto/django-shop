(function(angular, undefined) {
'use strict';

var module = angular.module('myshop.accordion', []);

module.directive('uibAccordionGroup', function() {
	return {
		restrict: 'EAC',
		require: '^djngFormsSet',
		link: function(scope, element, attrs, controller) {

			scope.panelIsDisabled = function() {
				return !controller.setIsValid;
			};
		}
	};
});

})(window.angular);
