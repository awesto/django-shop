(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.auth', []);

// Directive for element: <shop-auth-form ng-form action="...">
// handle a djangoSHOP's forms related to authentication
djangoShopModule.directive('shopAuthForm', ['$window', '$http', '$timeout',
                                   function($window, $http, $timeout) {
	return {
		restrict: 'E',
		require: 'form',
		scope: true,  // do not change this
		link: function(scope, element, attrs) {
			var timer = null;
			if (attrs.action === undefined)
				throw new Error("Form does not contain an `action` keyword");
			scope.success_message = scope.error_message = '';

			function proceedWithAction(response) {
				if (attrs.action === 'RELOAD_PAGE') {
					$window.location.reload();
				} else if (attrs.action === 'DO_NOTHING') {
					scope.success_message = response.success;
				} else {
					$window.location.href = attrs.action;
				}
			}

			// Submit auth form data. Use `delay` in milliseconds to postpone final action.
			scope.submitForm = function(submitURL, delay) {
				$http.post(submitURL, scope.form_data).success(function(response) {
					if (response.success) {
						scope.success_message = response.success;
						scope.error_message = '';
						timer = $timeout(function() {
							proceedWithAction(response);
							timer = null;
						}, delay);
					} else {
						proceedWithAction(response);
					}
				}).error(function(response) {
					// merge errors messages into a single one
					scope.error_message = '';
					angular.forEach(response, function(vals) {
						scope.error_message = scope.error_message.concat(vals);
					});
				});
			};

			scope.dismiss = function() {
				scope.error_message = scope.success_message = null;
			};

			scope.$on('$destroy', function(event) {
				if (timer) {
					$timeout.cancel(timer);
				}
			});
		}
	};
}]);

})(window.angular);
