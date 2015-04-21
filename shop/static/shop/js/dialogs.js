(function(angular, undefined) {

'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.dialogs', []);


// Directive <shop-dialog-booklet>
// It is used to add display the active booklet page and hide the remaining ones.
djangoShopModule.directive('shopDialogBooklet', ['$location', function($location) {
	var slugs = [];

	function breadcrumbClass(slug) {
		var current = slugs.indexOf(slug);
		var until = slugs.indexOf($location.path().replace('/', ''));
		return (current === 0 || until >= current) ? "btn-success" : "btn-default";
	}

	function disabledBreadcrumb(slug) {
		return false;
		var current = slugs.indexOf(slug);
		var until = slugs.indexOf($location.path().replace('/', ''));
		return (current !== 0 && until < current);
	}

	function displayBookletPage(slug) {
		var until = $location.path().replace('/', '');
		return !until || until === slug;
	}

	function collectSlug(anchor) {
		var elem = angular.element(anchor);
		if (elem.hasClass('btn')) {
			slugs.push(elem.attr('href').replace('#', ''));
		}
	}

	return {
		restrict: 'E',
		link: function(scope, element, attrs) {
			angular.forEach(element.find("a"), collectSlug);
			scope.breadcrumbClass = breadcrumbClass;
			scope.disabledBreadcrumb = disabledBreadcrumb;
			scope.displayBookletPage = displayBookletPage;
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
djangoShopModule.directive('shopDialogProceed', ['$window', function($window) {
	return {
		restrict: 'EA',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			DialogCtrl.isLoading = false;
			DialogCtrl.registerButton(element).then(function() {
				console.log("Proceed to: " + attrs.action);
				if (attrs.action === 'RELOAD_PAGE') {
					$window.location.reload();
				} else {
					$window.location.href = attrs.action;
				}
			}, null, function(errs) {
				console.error("The checkout form contains errors.");
				console.log(errs);
			});
		}
	};
}]);


djangoShopModule.directive('shopPurchaseButton', ['$window', '$http', '$q', 'djangoUrl',
                                                  function($window, $http, $q, djangoUrl) {
	var purchaseURL = djangoUrl.reverse('shop:checkout-purchase');
	return {
		restrict: 'EA',
		controller: 'DialogCtrl',
		link: function(scope, element, attrs, DialogCtrl) {
			DialogCtrl.isLoading = false;
			DialogCtrl.registerButton(element).then(function() {
				// cart update succeeded, the next step is to convert the cart into an order object
				return $http.post(purchaseURL, scope.data);
			}, null, function(errs) {
				console.error("Purchase form contains errors.");
				console.log(errs);
			}).then(function(response) {
				var expr = '$window.location.href="https://www.google.com/";'
				console.log(response.data.expression);
				// proceed on the PSPs server
				eval(response.data.expression);
			}, function(errs) {
				console.error("Unable to purchase.");
				console.log(errs);
			});
		}
	};
}]);

})(window.angular);
