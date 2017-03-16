(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.dialogs');

// The country can influence parameters for cart modifiers, hence we
// must upload the scope whenever this input fields changes
djangoShopModule.directive('shopAddressCountry', ['$q', function($q) {
	return {
		restrict: 'C',
		require: '^shopDialogForm',
		link: function(scope, element, attrs, DialogController) {
			scope.updateCountry = function() {
				var deferred = $q.defer();
				DialogController.uploadScope(scope, deferred);
				deferred.promise.then(function(response) {
					scope.data.shipping_address.is_pending = true;
				});
			};
		}
	};
}]);

})(window.angular);
