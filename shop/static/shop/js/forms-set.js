(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.forms-set', ['djng.urls', 'djng.forms']);


// Directive <ANY shop-forms-set ...>
// Use this as a wrapper around self validating <form ...> elements (see directive below), so that
// we can disable the proceed button whenever one of those forms does not validate.
// For dialog forms, such a proceed button can be rendered as:
// <button shop-dialog-proceed ng-click="proceedWith('PURCHASE_NOW')" ng-disabled="stepIsValid===false">Purchase Now</button>
djangoShopModule.directive('shopFormsSet', function() {
	return {
		require: 'shopFormsSet',
		scope: true,
		controller: ['$scope', function($scope) {
			var self = this;

			// a map of booleans keeping the validation state for each of the child forms
			this.digestValidatedForms = {};

			// check each child form's $valid state and reduce it to one single state scope.stepIsValid
			this.reduceValidation = function(formId, formIsValid) {
				self.digestValidatedForms[formId] = formIsValid;
				$scope.stepIsValid = true;
				angular.forEach(self.digestValidatedForms, function(validatedForm) {
					$scope.stepIsValid = $scope.stepIsValid && validatedForm;
				});
			};
		}]
	};
});


// Directive <ANY shop-forms-endpoint ...>
// Create a summary of one or more model scopes to be submitted to the given endpoint
djangoShopModule.directive('shopFormsEndpoint', ['$http', '$window', 'djangoForm', function($http, $window, djangoForm) {
	return {
		restrict: 'A',
		require: 'shopFormsEndpoint',
		scope: true,
		controller: ['$scope', function($scope) {
			var self = this;
			this.digestUploadScope = {};

			this.uploadScope = function(method, action, extraData) {
				// merge the data from various scope entities into one data object
				var data = {};
				angular.merge(data, extraData);
				angular.forEach(self.digestUploadScope, function(scopeModel) {
					angular.merge(data, $scope.$eval(scopeModel));
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
		link: function(scope, element, attrs, formEndpointController) {
			if (!attrs.shopFormsEndpoint)
				throw new Error("Attribute 'shop-forms-endpoint' does not declare any endpoint.");
			formEndpointController.uploadURL = attrs.shopFormsEndpoint;
		}
	};
}]);


// This directive enriches AngularJS's internal form-controller if it is wrapped inside a
// <ANY shop-forms-set ...> directive. Its only purpose is to summarize the validity of the given forms,
// so that buttons rendered outside of the forms can check the ``stepIsValid`` attribute.
djangoShopModule.directive('form', ['$timeout', function($timeout) {
	return {
		restrict: 'E',
		require: ['^?shopFormsSet', 'form'],
		priority: 1,
		link: function(scope, element, attrs, controllers) {
			var formsSetController = controllers[0], formController = controllers[1];

			if (!formsSetController)
				return;  // not for forms outside <ANY shop-forms-set></ANY shop-forms-set>

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


// This directive enriches AngularJS's internal form-controller if it is wrapped inside a
// <ANY shop-forms-endpoint ...> directive. Its only purpose is to summarize the scope-models
// of the given forms, so that the scope can be uploaded to the endpoint using one submission.
// Usage: <form name="my_name" scope-model="my_data" novalidate> where `my_data` is used to
// access the form's data inside the scope.
djangoShopModule.directive('form', function() {
	return {
		restrict: 'E',
		require: ['^?shopFormsEndpoint', 'form'],
		priority: 2,
		link: function(scope, element, attrs, controllers) {
			var formsEndpointController = controllers[0], formController = controllers[1];

			if (!formsEndpointController || !attrs.scopeModel)
				return;  // not for forms outside <ANY shop-forms-endpoint> element

			formsEndpointController.digestUploadScope[attrs.name] = attrs.scopeModel;
		}
	};
});


djangoShopModule.directive('shopEndpointProceed', function() {
	return {
		restrict: 'EA',
		require: '^shopFormsEndpoint',
		scope: true,
		link: function(scope, element, attrs, formsEndpointController) {
			if (attrs.extraData) {
				scope.extraData = scope.$eval(attrs.extraData) || attrs.extraData;
			}

			scope.create = function(action) {
				formsEndpointController.uploadScope('POST', action, scope.extraData);
			};

			scope.update = function(action) {
				formsEndpointController.uploadScope('PUT', action, scope.extraData);
			};
		}
	};
});


})(window.angular);
