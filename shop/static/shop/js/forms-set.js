(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.forms-set', ['djng.urls', 'djng.forms']);


// Directive <ANY shop-forms-set ...>
// Use this as a wrapper around self validating <form ...> elements (see directive below), so that
// we can disable the proceed button whenever one of those forms does not validate.
// Such a proceed button shall be rendered as:
// <button shop-dialog-proceed ng-click="proceedWith('PURCHASE_NOW')" ng-disabled="stepIsValid===false">Purchase Now</button>
djangoShopModule.directive('shopFormsSet', function() {
	return {
		require: 'shopFormsSet',
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


djangoShopModule.directive('form', ['$window', '$http', '$timeout', 'djangoForm', function($window, $http, $timeout, djangoForm) {
	return {
		restrict: 'E',
		require: ['^?shopFormsSet', 'form'],
		priority: 1,
		link: function(scope, element, attrs, controllers) {
			var uploadURL = attrs.action, scopeForm = scope[attrs.name], scopeData = scope[attrs.scopeModel];
			if (!controllers[0])
				return;  // not for forms outside <ANY shop-forms-digest></ANY shop-form-digest>

			function performSumission(action, method) {
				if (!uploadURL || !scopeForm || !scopeData)
					throw new URIError("One or more attributes are missing on this form declaration: 'action', 'name' or 'scope-model'");
				$http({
					url: uploadURL,
					method: method,
					data: scopeData
				}).then(function(response) {
					if (!djangoForm.setErrors(scopeForm, response.errors)) {
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
				}, function(response) {
					console.error(response);
				});
			}

			scope.create = function(action) {
				performSumission(action, 'POST');
			};

			scope.update = function(action) {
				performSumission(action, 'PUT');
			};

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
				controllers[0].reduceValidation(scope.$id, controllers[1].$valid);
			}
		}
	};
}]);


})(window.angular);
