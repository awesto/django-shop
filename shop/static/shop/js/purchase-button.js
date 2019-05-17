(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.purchase-button', ['djng.forms']);


// This special directive is used to initiate the purchasing operation from the client.
// First, the client calls the purchase-URL from the shop, from there it receives a JavaScript
// snippet, containing instructions on what to do next. Typically this is another http request onto
// the PSP's endpoint. Sometimes it is a redirect onto another page, hence the `$window` parameter
// has to be injected as well, even though unused.
module.directive('button', ['$http', '$log', '$q', '$rootScope', '$window', function($http, $log, $q, $rootScope, $window) {
	return {
		restrict: 'E',
		require: '^?djngFormsSet',
		link: function(scope, element, attrs, controller) {
			if (!controller)
				return;

			scope.purchaseNow = function(purchaseURL) {
				return function() {
					var deferred = $q.defer();
					$http.post(purchaseURL, {}).then(function(response) {
						// evaluate expression to proceed on the PSP's server which itself might be a promise
						eval(response.data.expression);
						deferred.resolve(response);
					}).catch(function(response) {
						if (response.status >= 400 && response.status <= 499) {
							scope.purchasingErrorMessage = response.data.purchasing_error_message;
						}
						deferred.reject(response);
					}).finally(function() {
						$rootScope.$broadcast('shop.messages.fetch');
					});
					return deferred.promise;
				}
			};
		}
	};
}]);


})(window.angular);
