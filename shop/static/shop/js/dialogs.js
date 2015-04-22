(function(angular, undefined) {

'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.dialogs', []);


// Shared controller for directives `shopDialogBookletSlug` and `shopDialogBookletPage`.
djangoShopModule.controller('DialogBookletCtrl', ['$scope', '$rootScope', function($scope, $rootScope) {
	if (!angular.isObject($rootScope.observedForms)) {
		$rootScope.observedForms = {_slugs: []};
	}
	$rootScope.observedForms[$scope.slug] = [];

	// add a form element to the list of observed forms, so that they can be checked for validity
	this.observeForms = function(formElem) {
		$rootScope.observedForms[$scope.slug].push(formElem.name);
	};

	this.pushSlug = function() {
		$rootScope.observedForms._slugs.push($scope.slug);
	};

	// Return true if all forms on this booklet page are valid
	function areFormsValid(slug) {
		var valid = true;
		angular.forEach($rootScope.observedForms[slug], function(form_name) {
			valid = valid && $rootScope[form_name].$valid;
		});
		return valid;
	};

	// Return true if this booklet page shall be editable. This implies that all previous
	// booklet pages have validated forms.
	this.bookletPageActive = function() {
		var active = true, k, slug;
		for (k = 0; k < $rootScope.observedForms._slugs.length; k++) {
			slug = $rootScope.observedForms._slugs[k];
			if (slug === $scope.slug || !active)
				break;
			active = areFormsValid(slug);
			console.log(slug + ': ' + active);
		}
		console.log($scope.slug + '= ' + active);
		console.log($rootScope);
		return active;
	};

	this.defaultPageActive = function() {
		console.log('defaultPageActive');
		var k, slug;
		for (k = 0; k < $rootScope.observedForms._slugs.length; k++) {
			slug = $rootScope.observedForms._slugs[k];
			if (!areFormsValid(slug))
				return slug === $scope.slug;
		}
		return slug === $scope.slug;
	};

}]);


// Directive <a shop-dialog-booklet-slug="slug" ...>
// It is used to display the active booklet button.
djangoShopModule.directive('shopDialogBookletButton', ['$compile', '$location', function($compile, $location) {
	return {
		restrict: 'E',
		controller: 'DialogBookletCtrl',
		scope: {
			slug: '@'
		},
		link: function(scope, element, attrs, ctrl) {
			var template = '<a ng-class="btnClass()" ng-click="btnClick()">' +
				angular.element(element).html() + '</a>';
			element.replaceWith($compile(template)(scope));
			ctrl.pushSlug();

			scope.btnClass = function() {
				return ctrl.bookletPageActive() ? "btn btn-success" : "btn btn-default disabled";
			};

			scope.btnClick = function() {
				if (ctrl.bookletPageActive()) {
					$location.path(scope.slug);
				}
			};
		}
	};
}]);


// Directive <TAG shop-dialog-booklet-page>
// It is used to display the active booklet page and to hide the remaining ones.
djangoShopModule.directive('shopDialogBookletPage', ['$compile', '$location', function($compile, $location) {
	return {
		restrict: 'E',
		controller: 'DialogBookletCtrl',
		scope: {
			slug: '@'
		},
		link: function(scope, element, attrs, ctrl) {
			var cssClass = attrs['class'] || '', cssStyle = attrs['style'] || '';
			var template = '<div ng-show="displayBookletPage()" class="' + cssClass + '" style="' + cssStyle + '">'
				+ angular.element(element).html() + '</div>';
			element.replaceWith($compile(template)(scope));
			angular.forEach(element.find("form"), ctrl.observeForms);

			scope.displayBookletPage = function() {
				var slug = $location.path().substr(1);
				return slug === scope.slug || !slug && ctrl.defaultPageActive();
			};
		}
	};
}]);


// Shared controller for all forms, links and buttons using shop-dialog elements. It just adds
// an `update` function to the scope, so that all forms can send their gathered data to the
// server. Since this controller does not make any presumption on how and where to proceed to,
// the caller has to set the controllers `deferred` to a `$q.deferred()` object.
djangoShopModule.controller('DialogCtrl', ['$scope', '$http', '$q', 'djangoUrl', 'djangoForm',
                                             function($scope, $http, $q, djangoUrl, djangoForm) {
	var self = this, updateURL = djangoUrl.reverse('shop:checkout-update');
	this.isLoading = true;  // prevent premature updates and re-triggering
	$scope.update = update;

	function update(deferred) {
		if (self.isLoading)
			return;
		self.isLoading = true;
		$http.post(updateURL, $scope.data).success(function(response) {
			var hasErrors = false;
			console.log(response);
			if (deferred) {
				// only report errors, when the customer clicked onto a button using the
				// directive `shop-dialog-proceed` or `shop-purchase-button`, but not on
				// ordinary update events.
				angular.forEach(response.errors, function(errors, key) {
					hasErrors = djangoForm.setErrors($scope[key], errors) || hasErrors;
				});
				if (hasErrors) {
					deferred.notify(response);
				} else {
					deferred.resolve(response);
				}
			}
			delete response.errors;
			$scope.cart = response;
		}).error(function(msg) {
			console.error("Unable to update checkout forms: " + msg);
		})['finally'](function() {
			self.isLoading = false;
		});
	}

	this.registerButton = function(element) {
		var deferred = $q.defer();
		element.on('click', function() {
			update(deferred);
		});
		element.on('$destroy', function() {
			element.off('click');
		});
		return deferred.promise;
	};

}]);


// Directive <form shop-dialog-form> (must be added as attribute to the <form> element)
// It is used to add an update() method to the scope's controller, so that `ng-change="update()"`
// can be added to any input element. Use it to update the models on the server.
djangoShopModule.directive('shopDialogForm', function() {
	return {
		restrict: 'A',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			DialogCtrl.isLoading = false;
		}
	};
});


// Directive to be added to button elements.
djangoShopModule.directive('shopDialogProceed', ['$window', '$location', '$http', '$q', 'djangoUrl',
                            function($window, $location, $http, $q, djangoUrl) {
	var purchaseURL = djangoUrl.reverse('shop:checkout-purchase');
	return {
		restrict: 'EA',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			DialogCtrl.isLoading = false;
			DialogCtrl.registerButton(element).then(function() {
				console.log("Proceed to: " + attrs.action);
				if (attrs.action === 'RELOAD_PAGE') {
					$window.location.reload();
				} else if (attrs.action === 'PURCHASE_NOW') {
					// convert the cart into an order object, this will propagate the promise
					return $http.post(purchaseURL, scope.data);
				} else if (attrs.action.substr(0, 1) === '#') {
					$location.path(attrs.action.substr(1));
					return $q.reject();
				} else {
					// proceed with new page
					$window.location.href = attrs.action;
				}
			}, null, function(errs) {
				console.error("The checkout form contains errors.");
				console.log(errs);
			}).then(function(response) {
				var expr = '$window.location.href="https://www.google.com/";'
				console.log(response.data.expression);
				// evaluate expression to proceed on the PSP's server
				eval(response.data.expression);
			}, function(errs) {
				if (errs) {
					console.error(errs);
				}
			});
		}
	};
}]);


})(window.angular);
