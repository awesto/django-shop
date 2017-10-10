(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.purchase-button', ['djng.forms']);


module.directive('button', ['$http', '$log', '$q', function($http, $log, $q) {
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
						$log.error(response.message);
						deferred.reject(response);
					});
					return deferred.promise;
				}
			};
		}
	};
}]);


})(window.angular);
