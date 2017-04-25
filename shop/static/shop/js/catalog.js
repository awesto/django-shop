(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.catalog', ['ui.bootstrap', 'django.shop.utils']);

djangoShopModule.controller('AddToCartCtrl', ['$scope', '$http', '$window', '$uibModal',
                                      function($scope, $http, $window, $uibModal) {
	var prevContext = null, updateUrl;

	this.setUpdateUrl = function(update_url) {
		updateUrl = update_url + $window.location.search;
	};

	this.loadContext = function() {
		$http.get(updateUrl).success(function(context) {
			prevContext = context;
			$scope.context = angular.copy(context);
		}).error(function(msg) {
			console.error('Unable to get context: ' + msg);
		});
	};

	$scope.updateContext = function() {
		if (angular.equals($scope.context, prevContext))
			return;
		$http.post(updateUrl, $scope.context).success(function(context) {
			prevContext = context;
			$scope.context = angular.copy(context);
		}).error(function(msg) {
			console.error('Unable to update context: ' + msg);
		});
	};

	$scope.addToCart = function(cart_url, extra_context) {
		$uibModal.open({
			templateUrl: 'AddToCartModalDialog.html',
			controller: 'ModalInstanceCtrl',
			resolve: {
				modal_context: function() {
					return {
						cart_url: cart_url,
						context: angular.extend(angular.isObject(extra_context) ? extra_context : {}, $scope.context)
					};
				}
			}
		}).result.then(function(next_url) {
			$window.location.href = next_url;
		});
	};

}]);

djangoShopModule.controller('ModalInstanceCtrl',
    ['$scope', '$http', '$uibModalInstance', 'modal_context',
    function($scope, $http, $uibModalInstance, modal_context) {
	var isLoading = false;
	$scope.proceed = function(next_url) {
		if (isLoading)
			return;
		isLoading = true;
		$http.post(modal_context.cart_url, $scope.context).success(function() {
			$uibModalInstance.close(next_url);
		}).error(function() {
			// TODO: tell us something went wrong
			$uibModalInstance.dismiss('cancel');
		}).finally(function() {
			isLoading = false;
		});
	};

	$scope.cancel = function () {
		$uibModalInstance.dismiss('cancel');
	};

	$scope.context = angular.copy(modal_context.context);
}]);


// Directive <ANY shop-add-to-cart="REST-API-endpoint">
// handle dialog box on the product's detail page to add a product to the cart
djangoShopModule.directive('shopAddToCart', function() {
	return {
		restrict: 'A',
		controller: 'AddToCartCtrl',
		link: function(scope, element, attrs, AddToCartCtrl) {
			if (!attrs.shopAddToCart)
				throw new Error("Directive shop-add-to-cart must point onto an URL");
			AddToCartCtrl.setUpdateUrl(attrs.shopAddToCart);
			AddToCartCtrl.loadContext();
		}
	};
});


djangoShopModule.controller('CatalogListController', [
    '$scope', '$http', 'djangoShop', function($scope, $http, djangoShop) {
	var self = this;

	this.loadProducts = function(config) {
		if ($scope.isLoading || $scope.fetchURL === null)
			return;
		$scope.isLoading = true;
		$http.get($scope.fetchURL, config).success(function(response) {
			$scope.fetchURL = response.next;
			$scope.catalog.count = response.count;
			$scope.catalog.products = $scope.catalog.products.concat(response.results);
			$scope.isLoading = false;
		}).error(function() {
			$scope.fetchURL = null;
			$scope.isLoading = false;
		});
	};

	this.resetProductsList = function() {
		$scope.fetchURL = djangoShop.getLocationPath();
		$scope.catalog.products = [];
	};

	$scope.loadMore = function() {
		var config = {params: djangoShop.paramsFromSearchQuery.apply(this, arguments)};
		console.log('load more products ...');
		self.loadProducts(config);
	};

	$scope.catalog = {};
	$scope.isLoading = false;
}]);


// Use directive <ANY shop-catalog-list infinite-scroll="true|false"> to wrap the content
// of the catalog's list views. If infinite scroll is true, use the scope function ``loadMore()``
// which shall be invoked by another directive, for instance <ANY in-view> when reaching the
// end of the listed items.
djangoShopModule.directive('shopCatalogList', ['$location', '$window', '$timeout', function($location, $window, $timeout) {
	return {
		restrict: 'EAC',
		controller: 'CatalogListController',
		link: function(scope, element, attrs, controller) {
			var infiniteScroll = scope.$eval(attrs.infiniteScroll);

			scope.$root.$on('shopCatalogSearch', function(event, params) {
				if (infiniteScroll) {
					controller.resetProductsList();
					controller.loadProducts({params: params});
				} else {
					$window.location.reload();
				}
			});

			scope.$root.$on('shopCatalogFilter', function(event, params) {
				if (infiniteScroll) {
					controller.resetProductsList();
					controller.loadProducts({params: params});
				} else {
					// delay until next digest cycle
					$timeout(function() {
						$location.search(params);
						scope.$digest();
						$window.location.reload();
					});
				}
			});

			controller.resetProductsList();
		}
	};
}]);

// Directive <ANY shop-sync-catalog="REST-API-endpoint">
// handle catalog list view combined with adding products to cart
djangoShopModule.directive('shopSyncCatalog', function() {
	return {
		restrict: 'A',
		controller: function() {},
		require: 'shopSyncCatalog',
		link: function(scope, element, attrs, controller) {
			if (angular.isUndefined(attrs['shopSyncCatalog']))
				throw new Error("Directive shop-sync-catalog must point onto an URL");
			controller.syncCatalogUrl = attrs.shopSyncCatalog;
		}
	};
});


// Directive <ANY shop-sync-catalog-item="member-of-current-$scope">
// This directive must be a child of <ANY shop-sync-catalog ...>.
// It can be used to synchronize the local scope of a catalog item, for instance to set the
// quantity of an item in the cart. This directive normally is used to sync cart items from the
// catalog list view.
djangoShopModule.directive('shopSyncCatalogItem', function() {
	return {
		restrict: 'A',
		require: ['^shopSyncCatalog', 'shopSyncCatalogItem'],
		scope: true,
		controller: ['$scope', '$http', function($scope, $http) {
			var self = this, prev_item = null, isLoading = false;

			$scope.syncQuantity = function() {
				if (isLoading || angular.equals($scope.catalog_item, prev_item))
					return;
				isLoading = true;
				$http.post(self.parent.syncCatalogUrl, $scope.catalog_item).success(function(response) {
					var cart = response.cart;
					delete response.cart;
					prev_item = response;
					angular.extend($scope.catalog_item, response);
					$scope.$emit('shopUpdateCarticonCaption', cart);
					isLoading = false;
				}).error(function(msg) {
					console.error('Unable to sync quantity: ' + msg);
					isLoading = false;
				});
			};

		}],
		link: function(scope, element, attrs, controllers) {
			if (angular.isUndefined(attrs['shopSyncCatalogItem']))
				throw new Error("Directive shop-sync-catalog-item must provide an initialization object");
			controllers[1].parent = controllers[0];
			scope.catalog_item = scope.$eval(attrs.shopSyncCatalogItem);
		}
	};
});


})(window.angular);
