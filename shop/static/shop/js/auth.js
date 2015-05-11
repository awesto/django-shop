(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.auth', []);

// Directive <shop-auth-form>
// handle a djangoSHOP's forms related to authentication
djangoShopModule.directive('shopAuthForm', ['$window', '$http', function($window, $http) {
	return {
		restrict: 'A',
		require: 'form',
		scope: true,
		link: function(scope, element, attrs, formCtrl) {
			if (attrs.action === undefined)
				throw new Error("Form does not contain an `action` keyword");

			scope.submit = function(submitURL) {
				$http.post(submitURL, scope.form_data).success(function(response) {
					if (attrs.action === 'RELOAD_PAGE') {
						$window.location.reload();
					} else if (attrs.action === 'DO_NOTHING') {
						scope.success_message = response.success;
					} else {
						$window.location.href = attrs.action;
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
		}
	};
}]);

})(window.angular);
