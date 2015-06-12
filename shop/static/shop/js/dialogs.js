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


// Directive <shop-booklet-wrapper ...> to be used with booklet forms.
djangoShopModule.directive('shopBookletWrapper', ['$controller', '$window', '$http', '$q',
                                          function($controller, $window, $http, $q) {
	return {
		restrict: 'E',
		scope: true,
		controller: function($scope) {
			var self = this;

			// add a form elements to the list of observed forms, so that they can be checked for validity
			self.observeForms = function(formElem) {
				if (!angular.isArray($scope.observedForms[this.pagenum])) {
					$scope.observedForms[this.pagenum] = {formElems: []};
				}
				//if (formElem.attributes.nonalidate) {
					// only observe forms, which do not know how to validate themselves
					$scope.observedForms[this.pagenum].formElems.push(formElem);
				//}
			};

			self.setValidity = function(pagenum, validity) {
				$scope.observedForms[pagenum].validity = validity;
			}

			self.getActivePage = function() {
				return $scope.activePage;
			};

			self.setNextActivePage = function() {
				if (angular.isObject($scope.observedForms[$scope.activePage + 1])) {
					// proceed with next booklet page
					$scope.activePage++;
					return true;
				}
			};

			$scope.breadcrumbClass = function(pagenum) {
				var display_as_valid = true, display_as_valid_prev, k;
				//console.log(' pagenum = ', pagenum);
				//console.log($scope.observedForms[pagenum]);
				for (k = 0; k <= pagenum; k++) {
					display_as_valid_prev = display_as_valid;
					display_as_valid = display_as_valid && $scope.observedForms[k] && $scope.observedForms[k].validity;
				}
				if (display_as_valid)
					return "btn btn-success";
				if (display_as_valid_prev)
					return "btn btn-primary";
				return "btn btn-default disabled";
			};

			$scope.breadcrumbClick = function(pagenum) {
				if (pagenum == 0 || $scope.observedForms[pagenum - 1].validity || $scope.observedForms[pagenum].validity) {
					$scope.activePage = pagenum;
				}
			};

		},
		link: {
			pre: function(scope, element, attrs, controller) {
				controller.dialogCtrl = $controller('DialogCtrl', {$scope: scope});
				scope.observedForms = {};
			},
			post: function(scope, element, attrs, controller) {
				scope.activePage = 0;
				scope.bookletAction = attrs.action;
				console.log(scope.observedForms);
			}
		}
	};
}]);


// Directive <TAG shop-booklet-page>
// It is used to display the active booklet page and to hide the remaining ones.
djangoShopModule.directive('shopBookletPage', ['$compile', '$window', '$http', '$q', '$timeout', 'djangoUrl',
                                       function($compile, $window, $http, $q, $timeout, djangoUrl) {
	var purchaseURL = djangoUrl.reverse('shop:checkout-purchase');
	return {
		restrict: 'E',
		require: ['^shopBookletWrapper', 'shopBookletPage'],
		scope: true,
		controller: function($scope) {
			// return true if all forms for this booklet wrapper are valid
			this.areFormsValid = function(pagenum) {
				return true;

				var valid = true;
				angular.forEach($scope.observedForms[pagenum].formElems, function(formElem) {
					if (formElem.noValidate) {
						valid = valid && $scope[formElem.name].$valid;
					}
				});
				return valid;
			};
		},
		link: {
			pre: function(scope, element, attrs, controllers) {
				//console.log(element); console.log(element.find("form"));
				//angular.forEach(element.find("form"), controllers[0].observeForms, attrs);
				// scope.pagenum = attrs.pagenum; we don't need this
			},
			post: function(scope, element, attrs, controllers) {
				var bookletCtrl = controllers[0], pageController = controllers[1];
				var cssClasses = attrs['class'] ? ' class="' + attrs['class'] + '"' : '';
				var cssStyles = attrs['style'] ? ' style="' + attrs['style'] + '"' : '';
				var template = '<div ng-show="showBookletPage()"' + cssClasses + cssStyles + '>'
					+ angular.element(element).html() + '</div>';
				element.replaceWith($compile(template)(scope));

				$timeout(function() {
					// wait until every form is ready
					//bookletCtrl.setValidity(attrs.pagenum, pageController.areFormsValid(attrs.pagenum));
					angular.forEach(element.find("form"), function(formElem) {
						console.log(formElem);
						console.log(scope[formElem.name]);
					});
				});

				scope.showBookletPage = function() {
					return bookletCtrl.getActivePage() == attrs.pagenum;
				};

				scope.buttonClass = function() {
					return pageController.areFormsValid(attrs.pagenum) ? "" : "disabled";
				};

				scope.submitPage = function() {
					var deferred = $q.defer();
					if (pageController.areFormsValid(attrs.pagenum)) {
						bookletCtrl.dialogCtrl.uploadScope(scope, deferred);
						deferred.promise.then(function(response) {
							console.log(response);
							bookletCtrl.setValidity(attrs.pagenum, true);
							bookletCtrl.setNextActivePage();
						}, function(response) {
							console.log(response);
						});
					}
				};

				scope.submitBooklet = function() {
					var deferred = $q.defer();
					if (pageController.areFormsValid(attrs.pagenum)) {
						bookletCtrl.dialogCtrl.uploadScope(scope, deferred);
						deferred.promise.then(function(response) {
							console.log(response);
							// finally, proceed with link as specified in booklet wrapper
							if (scope.bookletAction === 'RELOAD_PAGE') {
								$window.location.reload();
							} else if (scope.bookletAction === 'PURCHASE_NOW') {
								// Convert the cart into an order object.
								// This will propagate the promise to the success handler below.
								return $http.post(purchaseURL, scope.data);
							} else {
								// Proceed as usual and load another page
								$window.location.href = scope.bookletAction;
							}
						}).then(function(response) {
							console.log(response.data);
							// evaluate expression to proceed on the PSP's server
							eval(response.data.expression);
						}, function(response) {
							if (response.errors) {
								console.error(response.errors);
							}
						}, function() {
							console.log('notified');
						});
					}
				};

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
