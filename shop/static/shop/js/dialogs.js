(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.dialogs', ['djng.urls', 'djng.forms', 'django.shop.utils']);


// Shared controller for all forms, links and buttons using shop-dialog elements. It just adds
// an `upload` function to the scope, so that all forms can send their gathered data to the
// server. Since this controller does not make any presumption on how and where to proceed to,
// the caller has to set the controllers `deferred` to a `$q.deferred()` object.
djangoShopModule.controller('DialogController',
        ['$scope', '$rootScope', '$http', '$q', 'djangoUrl', 'djangoForm',
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
			$rootScope.cart = response.cart;
			$rootScope.checkout_summary = response.checkout_summary;
		}).error(function(errors) {
			console.error("Unable to upload checkout forms:");
			console.log(errors);
		});
	};

	// This function is a noop returning a the promise of the given deferred object for further
	// processing. Its only purpose is to add a hook in case intermediate asynchronous operations
	// are required, as in the case of the external dialog form used by djangoshop-stripe.
	function prepare(deferred) {
		deferred.resolve();
		return deferred.promise;
	}

	$scope.prepare = $scope.prepare || prepare;
}]);


// Directive <form shop-dialog-form ...> (must be added as attribute to the <form> element)
// It is used to add an `upload()` method to the scope, so that `ng-change="upload()"`
// can be added to any input element. Use it to upload the models on the server.
djangoShopModule.directive('shopDialogForm', ['$q', '$timeout', function($q, $timeout) {
	return {
		restrict: 'A',
		controller: 'DialogController',
		link: function(scope, element, attrs, DialogController) {
			var ready = false;
			if (attrs.shopDialogForm) {
				// initialize with form data
				scope.$eval(attrs.shopDialogForm);
			}
			$timeout(function() {
				// form ran its first scope.$digest() cycle
				ready = true;
			});

			scope.upload = function() {
				if (ready) {
					DialogController.uploadScope(scope);
				}
			};

			scope.switchEntity = function(form_controller) {
				var deferred;
				if (ready) {
					deferred = $q.defer();
					DialogController.uploadScope(scope, deferred);
					deferred.promise.then(pristineEntity, pristineEntity);
				}

				function pristineEntity(response) {
					angular.extend(scope.data, response.data);
					scope.stepIsValid = response.data.$valid;
					form_controller.$setPristine();
				}
			};

			scope.removeEntity = function(form_controller, data_model) {
				var deferred = $q.defer();
				if (angular.isObject(scope.data[data_model])) {
					scope.data[data_model].remove_entity = true;
					DialogController.uploadScope(scope, deferred);
				}
				if (angular.isObject(form_controller['form_entities'])) {
					$q.when(deferred.promise).then(function(response) {
						var remove_entity_filter;
						if (angular.isObject(response.data[data_model]) && angular.isString(response.data[data_model].remove_entity_filter)) {
							remove_entity_filter = new Function(response.data[data_model].remove_entity_filter);
							form_controller['form_entities'] = remove_entity_filter.apply(null, form_controller['form_entities']);
						}
						scope.stepIsValid = response.data.$valid;
						angular.extend(scope.data, response.data);
						// skip one digest cycle so that the form can be updated without triggering a change event
						ready = false; $timeout(function() { ready = true; });
					});
				}
			};
		}
	};
}]);


// Directive <ANY shop-dialog-proceed> to be added to button elements.
djangoShopModule.directive('shopDialogProceed', ['$window', '$http', '$q', 'djangoUrl',
                                         function($window, $http, $q, djangoUrl) {
	var purchaseURL = djangoUrl.reverse('shop:checkout-purchase');
	return {
		restrict: 'EA',
		controller: 'DialogController',
		link: function(scope, element, attrs, DialogController) {
			// add ng-click="proceed()" to button elements wishing to post the content of the
			// current scope. Returns a promise for further processing.
			scope.proceed = function() {
				var deferred = $q.defer();  // deferred for uploading scope
				scope.prepare($q.defer()).then(function() {
					DialogController.uploadScope(scope, deferred);
				});
				return deferred.promise;
			};

			// add ng-click="proceedWith(action)" to button elements wishing to
			// proceed after having posted the content of the current scope.
			scope.proceedWith = function(action) {
				scope.prepare($q.defer()).then(function() {
					var deferred = $q.defer();  // deferred for uploading scope
					DialogController.uploadScope(scope, deferred);
					performAction(deferred.promise, action);
				});
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
						$window.location.assign(action);
					}
				}).then(function(response) {
					if (response) {
						console.log(response);
						// evaluate expression to proceed on the PSP's server which itself might be a promise
						return eval(response.data.expression);
					}
				}).then(function() {
					console.log("Proceeded without any further request-response cycle.");
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


// Directive <ANY shop-forms-digest ...>
// Use this as a wrapper around self validating <form ...> elements (see directive below), so that
// we can disable the proceed button whenever one of those forms does not validate.
// Such a proceed button shall be rendered as:
// <button shop-dialog-proceed ng-click="proceedWith('PURCHASE_NOW')" ng-disabled="stepIsValid===false">Purchase Now</button>
djangoShopModule.directive('shopFormsDigest', function() {
	return {
		require: 'shopFormsDigest',
		scope: true,
		controller: function($scope) {
			// check each child form's $valid state and reduce it to one single state scope.stepIsValid
			this.reduceValidation = function(formId, formIsValid) {
				$scope.digestValidatedForms[formId] = formIsValid;
				$scope.stepIsValid = true;
				angular.forEach($scope.digestValidatedForms, function(validatedForm) {
					$scope.stepIsValid = $scope.stepIsValid && validatedForm;
				});
			};
		},
		link: {
			pre: function(scope) {
				// a map of booleans keeping the validation state for each of the child forms
				scope.digestValidatedForms = {};
			}
		}
	};
});

djangoShopModule.directive('form', ['$timeout', function($timeout) {
	return {
		restrict: 'E',
		require: ['^?shopFormsDigest', 'form'],
		priority: 1,
		scope: {},
		link: function(scope, element, attrs, controllers) {
			if (!controllers[0])
				return;  // not for forms outside <ANY shop-forms-digest></ANY shop-form-digest>

			element.find('input').on('keyup change', function() {
				// delay until validation is ready
				$timeout(reduceValidation);
			});
			element.find('select').on('change', function() {
				$timeout(reduceValidation);
			});
			element.find('textarea').on('blur', function() {
				$timeout(reduceValidation);
			});

			// delay first evaluation until form is fully validated
			$timeout(reduceValidation);

			function reduceValidation() {
				controllers[0].reduceValidation(scope.$id, controllers[1].$valid);
			}
		}
	};
}]);


})(window.angular);
