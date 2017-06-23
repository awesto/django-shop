(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.forms-set', ['djng.urls', 'djng.forms']);


// Directive <ANY shop-forms-set upload-url="/rest/endpoint" ...>, optionally with a REST endpoint.
// Use this as a wrapper around self validating <form ...> elements (see directive below), so that
// we can disable the proceed button whenever one of those forms does not validate.
// For dialog forms, such a proceed button can be rendered as:
// <button ng-click="update('PURCHASE_NOW')" ng-disabled="stepIsValid===false">Submit</button>
djangoShopModule.directive('shopFormsSet', function() {
	return {
		require: 'shopFormsSet',
		scope: true,
		controller: ['$scope', '$http', '$window', 'djangoForm', function($scope, $http, $window, djangoForm) {
			var self = this;

			// a map of booleans keeping the validation state for each of the child forms
			this.digestValidatedForms = {};

			// dictionary of form names mapping their model scopes
			this.digestUploadScope = {};

			// check each child form's $valid state and reduce it to one single state scope.stepIsValid
			this.reduceValidation = function(formId, formIsValid) {
				self.digestValidatedForms[formId] = formIsValid;
				$scope.stepIsValid = true;
				angular.forEach(self.digestValidatedForms, function(validatedForm) {
					$scope.stepIsValid = $scope.stepIsValid && validatedForm;
				});
			};

			this.uploadScope = function(method, action, extraData) {
				if (!self.uploadURL)
					throw new Error("Can not upload form data: Missing attribute 'upload-url'");

				// merge the data from various scope entities into one data object
				var data = {};
				if (extraData) {
					angular.merge(data, extraData);
				}
				angular.forEach(self.digestUploadScope, function(scopeModel) {
					var modelScope = {}, value = $scope.$eval(scopeModel);
					if (value) {
						modelScope[scopeModel] = value;
						angular.merge(data, modelScope);
					}
				});

				// submit data from all forms below this endpoint to the server
				$http({
					url: self.uploadURL,
					method: method,
					data: data
				}).then(function(response) {
					angular.forEach(self.digestUploadScope, function(scopeModel, formName) {
						if (!djangoForm.setErrors($scope[formName], response.errors)) {
							if (action === 'RELOAD_PAGE') {
								$window.location.reload();
							} else if (action !== 'DO_NOTHING') {
								if (response.data.success_url) {
									$window.location.assign(response.data.success_url);
								} else {
									$window.location.assign(action);
								}
							}
						}
					});
				}, function(response) {
					console.error(response);
				});
			};
		}],
		link: function(scope, element, attrs, formsSetController) {
			if (attrs.shopUploadUrl) {
				formsSetController.uploadURL = attrs.shopUploadUrl;
			}
		}
	};
});


// This directive enriches AngularJS's internal form-controller if it is wrapped inside a
// <ANY shop-forms-set ...> directive. One purpose is to summarize the validity of the given forms, so that buttons
// rendered outside of the <form ...> element but inside the <ANY shop-forms-set ...> element can check the
// ``stepIsValid`` attribute.
// Another purpose of this directive is to summarize the scope-models of the given forms, so that the scope can
// be uploaded to the endpoint URL using one submission.
// Usage: <form name="my_name" scope-model="my_data" novalidate> where `my_data` is used to access the form's
// data inside the scope.
djangoShopModule.directive('form', ['$timeout', function($timeout) {
	return {
		restrict: 'E',
		require: ['^?shopFormsSet', 'form'],
		priority: 1,
		link: function(scope, element, attrs, controllers) {
			var formsSetController = controllers[0], formController = controllers[1];

			if (!formsSetController)
				return;  // not for forms outside <ANY shop-forms-set></ANY shop-forms-set>

			if (attrs.name && attrs.scopeModel) {
				formsSetController.digestUploadScope[attrs.name] = attrs.scopeModel;
			}

			// create new isolated scope for this form
			scope = scope.$new(true);

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
				formsSetController.reduceValidation(scope.$id, formController.$valid);
			}
		}
	};
}]);



// This directive enriches the button element if it is wrapped inside a <ANY shop-forms-set ...> directive.
// It adds to functions to its scope ``create`` and ``update`` which shall be used to invoke a POST or
// PUT request on the forms-set endpoint URL.
// Optionally one can add ``shop-extra-data="..."`` to this button element, in order to pass further information
// to the given endpoint.
djangoShopModule.directive('button', function() {
	return {
		restrict: 'E',
		require: '^?shopFormsSet',
		scope: true,
		link: function(scope, element, attrs, formsSetController) {
			if (!formsSetController)
				return;  // not for buttons outside <ANY shop-forms-set></ANY shop-forms-set>

			scope.create = function(action) {
				formsSetController.uploadScope('POST', action, scope.shopExtraData);
			};

			scope.update = function(action) {
				formsSetController.uploadScope('PUT', action, scope.shopExtraData);
			};

			if (attrs.shopExtraData) {
				scope.shopExtraData = scope.$eval(attrs.shopExtraData) || attrs.shopExtraData;
			}
		}
	};
});


})(window.angular);
