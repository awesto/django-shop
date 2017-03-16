(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.auth', []);

// Directive for element: <shop-auth-form ng-form action="...">
// handle a django-SHOP's forms related to authentication
djangoShopModule.directive('shopAuthForm', ['$window', '$http', '$timeout',
                                   function($window, $http, $timeout) {
	return {
		restrict: 'E',
		require: 'form',
		scope: true,  // do not change this
		link: function(scope, element, attrs) {
			var timer = null, form = scope[attrs.name];
			if (angular.isUndefined(attrs.action))
				throw new Error("Form does not contain an `action` keyword");
			if (angular.isUndefined(form))
				throw new Error("Form has no `name`");
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
				submitURL = submitURL || attrs.formSubmitUrl;
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
					if (!form) {
						console.error("Please provide a name for this form");
						return;
					}
					scope.error_message = '';
					angular.forEach(response, function(vals, field) {
						var message = vals[0];
						if (angular.isObject(form[field])) {
							if (message.length < 50) {
								form[field].$message = message;
							} else {
								// display larger error messages inside the non-fields error box
								scope.error_message = scope.error_message.concat(vals);
							}
							form[field].$setValidity('rejected', false);
							form[field].$setPristine();
						} else {
							scope.error_message = scope.error_message.concat(vals);
						}
					});
				});
			};

			scope.hasError = function(field) {
				if (angular.isObject(form[field])) {
					if (form[field].$pristine) {
						if (form[field].$error.rejected)
							return 'has-error';
					} else {
						form[field].$setValidity('rejected', true);
						if (form[field].$invalid)
							return 'has-error';
					}
				}
			};


			scope.dismiss = function() {
				scope.error_message = scope.success_message = null;
			};

			scope.$on('$destroy', function(event) {
				if (timer) {
					$timeout.cancel(timer);
				}
			});

			element.bind('keyup', function(event) {
				if (event.which === 13) {
					// trigger on pressed Enter key
					scope.$apply(function() {
						scope.$eval(scope.submitForm());
					});
					event.preventDefault();
				}
			});
		}
	};
}]);

})(window.angular);
