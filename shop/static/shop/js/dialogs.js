(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.dialogs', ['ng.django.urls', 'ng.django.forms']);


// Shared controller for all forms, links and buttons using shop-dialog elements. It just adds
// an `upload` function to the scope, so that all forms can send their gathered data to the
// server. Since this controller does not make any presumption on how and where to proceed to,
// the caller has to set the controllers `deferred` to a `$q.deferred()` object.
djangoShopModule.controller('DialogCtrl', ['$scope', '$rootScope', '$http', '$q', 'djangoUrl', 'djangoForm',
                                   function($scope, $rootScope, $http, $q, djangoUrl, djangoForm) {
	var uploadURL = djangoUrl.reverse('shop:checkout-upload');

	function getProperty(obj, prop) {
		var parts = prop.split('.'), part;
		for (part = parts.shift(); obj && part; part = parts.shift()) {
			obj = obj[part];
		}
		return obj;
	}

	this.uploadScope = function(scope, deferred) {
		$http.post(uploadURL, scope.data).success(function(response) {
			var hasErrors = false;
			if (deferred) {
				// only report errors, when the customer clicked onto a button using the
				// directive `shop-dialog-proceed`, but not on ordinary upload events.
				angular.forEach(response.errors, function(errors, key) {
					var errProp = getProperty(scope, key);
					hasErrors = djangoForm.setErrors(errProp, errors) || hasErrors;
				});
				if (hasErrors) {
					deferred.reject(response);
				} else {
					deferred.resolve(response);
				}
			}
			// TODO: use $scope.$root instead of $rootScope
			$rootScope.cart = response;
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


// Directive shop-dialog-proceed to be added to button elements.
djangoShopModule.directive('shopDialogProceed', ['$window', '$http', '$q', 'djangoUrl',
                         function($window, $http, $q, djangoUrl) {
	var purchaseURL = djangoUrl.reverse('shop:checkout-purchase');
	return {
		restrict: 'EA',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			// add ng-click="proceed()" to button elements wishing to post the content of the
			// current scope. Returns a promise for further processing.
			scope.proceed = function() {
				var deferred = $q.defer();
				DialogCtrl.uploadScope(scope, deferred);
				return deferred.promise;
			};

			// add ng-click="proceedWith(action)" to button elements wishing to
			// proceed after having posted the content of the current scope.
			scope.proceedWith = function(action) {
				var deferred = $q.defer();
				DialogCtrl.uploadScope(scope, deferred);
				performAction(deferred.promise, action);
			};

			// Some actions, such as purchasing require a lot of time. This function
			// disables the button and replaces existing Glyphicons against a spinning wheel.
			function disableButton() {
				element.attr('disabled', 'disabled');
				angular.forEach(element.find('span'), function(span) {
					span = angular.element(span);
					if (span.hasClass('glyphicon')) {
						span.attr('deactivated-class', span.attr('class'));
						span.attr('class', 'glyphicon glyphicon-refresh glyphicon-refresh-animate');
					}
				});
			}

			function reenableButton() {
				element.removeAttr('disabled');
				angular.forEach(element.find('span'), function(span) {
					span = angular.element(span);
					if (span.attr('deactivated-class')) {
						span.attr('class', span.attr('deactivated-class'));
						span.removeAttr('deactivated-class');
					}
				});
			}

			function performAction(promise, action) {
				$q.when(promise).then(function() {
					console.log("Proceed to: " + action);
					if (action === 'RELOAD_PAGE') {
						$window.location.reload();
					} else if (action === 'PURCHASE_NOW') {
						disableButton();
						// Convert the cart into an order object.
						return $http.post(purchaseURL, scope.data);
					} else {
						// Proceed as usual and load another page
						$window.location.href = action;
					}
				}).then(function(response) {
					var result;
					if (response) {
						console.log(response);
						// evaluate expression to proceed on the PSP's server which itself might be a promise
						return eval(response.data.expression);
					}
				}).then(function() {
					console.log("Purchased without any further request-response cycle.");
				}, function(errs) {
					if (errs) {
						console.error(errs);
					}
					reenableButton();
				});
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
