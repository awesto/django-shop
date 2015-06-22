(function(angular, undefined) {

'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.dialogs', []);


// Shared controller for all forms, links and buttons using shop-dialog elements. It just adds
// an `upload` function to the scope, so that all forms can send their gathered data to the
// server. Since this controller does not make any presumption on how and where to proceed to,
// the caller has to set the controllers `deferred` to a `$q.deferred()` object.
djangoShopModule.controller('DialogCtrl', ['$scope', '$http', '$q', 'djangoUrl', 'djangoForm',
                                   function($scope, $http, $q, djangoUrl, djangoForm) {
	var self = this, uploadURL = djangoUrl.reverse('shop:checkout-upload');

	this.uploadScope = function(scope, deferred) {
		$http.post(uploadURL, scope.data).success(function(response) {
			var hasErrors = false;
			if (deferred) {
				// only report errors, when the customer clicked onto a button using the
				// directive `shop-dialog-proceed`, but not on ordinary upload events.
				angular.forEach(response.errors, function(errors, key) {
					hasErrors = djangoForm.setErrors(scope[key], errors) || hasErrors;
				});
				if (hasErrors) {
					deferred.reject(response);
				} else {
					deferred.resolve(response);
				}
			}
			$scope.cart = response;
		}).error(function(errors) {
			console.error("Unable to upload checkout forms:");
			console.log(errors);
		});
	};

}]);


// Directive <form shop-dialog-form> (must be added as attribute to the <form> element)
// It is used to add an `upload()` method to the scope, so that `ng-change="upload()"`
// can be added to any input element. Use it to upload the models on the server.
djangoShopModule.directive('shopDialogForm', function() {
	return {
		restrict: 'A',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			scope.upload = function() {
				DialogCtrl.uploadScope(scope);
			};
		}
	};
});


// Directive to be added to button elements.
djangoShopModule.directive('shopDialogProceed', ['$window', '$http', '$q', 'djangoUrl',
                         function($window, $http, $q, djangoUrl) {
	var purchaseURL = djangoUrl.reverse('shop:checkout-purchase');
	return {
		restrict: 'EA',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			scope.proceedWith = function(action) {
				var deferred = $q.defer();
				DialogCtrl.uploadScope(scope, deferred);
				deferred.promise.then(function() {
					console.log("Proceed to: " + action);
					if (action === 'RELOAD_PAGE') {
						$window.location.reload();
					} else if (action === 'PURCHASE_NOW') {
						// Convert the cart into an order object.
						return $http.post(purchaseURL, scope.data);
					} else {
						// Proceed as usual and load another page
						$window.location.href = action;
					}
				}).then(function(response) {
					console.log(response.data);
					// evaluate expression to proceed on the PSP's server
					eval(response.data.expression);
				}, function(errs) {
					if (errs) {
						console.error(errs);
					}
				});
			};

		}
	};
}]);


			}
		}
	};
}]);


// Directive <TAG shop-form-validate="model-to-watch">
// It is used to override the validation of hidden form fragments.
// If model-to-watch is false, then input elements inside this DOM tree are not validated.
// This is useful, if a form fragment shall be validated only under certain conditions.
djangoShopModule.directive('shopFormValidate', function() {
	return {
		restrict: 'A',
		require: '^form',
		link: function(scope, element, attrs, formCtrl) {
			if (!attrs.shopFormValidate)
				return;
			scope.$watch(attrs.shopFormValidate, function() {
				var validateExpr = scope.$eval(attrs.shopFormValidate);
				angular.forEach(formCtrl, function(instance) {
					// iterate over form controller and move active parsers to inactive
					if (angular.isObject(instance) && instance.hasOwnProperty('$parsers')) {
						if (validateExpr) {
							if (angular.isArray(instance.$inactiveParsers)) {
								instance.$parsers = instance.$inactiveParsers;
							}
							instance.$inactiveParsers = [];
						} else {
							instance.$inactiveParsers = instance.$parsers;
							instance.$parsers = [];
							// reset all possible errors for this input element
							angular.forEach(instance.$error, function(val, key) {
								instance.$setValidity(key, true);
							});
						}
					}
				});
			});
		}
	};
});


})(window.angular);
