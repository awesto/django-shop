(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.order', []);

// Directive <form shop-order-form ...> (must be added as attribute to the <form> element)
// It is used to add an `upload()` method to the scope, so that `ng-change="upload()"`
// can be added to any input element. Use it to upload the models on the server using
// method 'POST' on the current request path as it's REST-API endpoint.
djangoShopModule.directive('shopOrderForm', ['$http', '$window', function($http, $window) {
	return {
		restrict: 'A',
		require: 'form',
		scope: true,
		link: function (scope, element, attrs, controller) {
			if (attrs.shopOrderForm) {
				// initialize with form data
				scope.$eval(attrs.shopOrderForm);
			};
			scope.update = function(action) {
				$http.post($window.location, scope.data).success(function(response) {
					if (action) {
						$window.location.assign(action);
					} else {
						angular.extend(scope.data, response.data);
					}
				});
			}
		}
	};
}]);

})(window.angular);;
