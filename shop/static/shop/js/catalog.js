(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.catalog', ['ui.bootstrap', 'django.shop.utils']);

djangoShopModule.controller('AddToCartCtrl', ['$scope', '$http', '$window', '$modal',
                                               function($scope, $http, $window, $modal) {
	var isLoading = false, prevContext = null, updateUrl;

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
		if (isLoading || angular.equals($scope.context, prevContext))
			return;
		isLoading = true;
		$http.post(updateUrl, $scope.context).success(function(context) {
			prevContext = context;
			$scope.context = angular.copy(context);
		}).error(function(msg) {
			console.error('Unable to update context: ' + msg);
		}).finally(function() {
			isLoading = false;
		});
	};

	$scope.addToCart = function(cart_url, extra_context) {
		$modal.open({
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

djangoShopModule.controller('ModalInstanceCtrl', ['$scope', '$http', '$modalInstance', 'modal_context',
                                        function($scope, $http, $modalInstance, modal_context) {
	var isLoading = false;
	$scope.proceed = function(next_url) {
		if (isLoading)
			return;
		isLoading = true;
		$http.post(modal_context.cart_url, $scope.context).success(function() {
			$modalInstance.close(next_url);
		}).error(function() {
			// TODO: tell us something went wrong
			$modalInstance.dismiss('cancel');
		}).finally(function() {
			isLoading = false;
		});
	};

	$scope.cancel = function () {
		$modalInstance.dismiss('cancel');
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


djangoShopModule.controller('CatalogListController', ['$scope', '$http', 'djangoShop', function($scope, $http, djangoShop) {
	var self = this, fetchURL = djangoShop.getLocationPath();

	this.loadProducts = function(config) {
		if ($scope.isLoading || fetchURL === null)
			return;
		$scope.isLoading = true;
		$http.get(fetchURL, config).success(function(response) {
			fetchURL = response.next;
			$scope.catalog.count = response.count;
			$scope.catalog.products = $scope.catalog.products.concat(response.results);
			$scope.isLoading = false;
		}).error(function() {
			fetchURL = null;
			$scope.isLoading = false;
		});
	}

	$scope.loadMore = function() {
		var config = {params: djangoShop.paramsFromSearchQuery.apply(this, arguments)};
		console.log('load more products ...');
		self.loadProducts(config);
	};

	// listen on events of type `shopCatalogSearch`
	$scope.$root.$on('shopCatalogSearch', function(event, config) {
		try {
			config = {params: {autocomplete: config.params.q}};
		} catch (err) {
			config = null;
		}
		fetchURL = djangoShop.getLocationPath() + 'search-catalog';
		$scope.catalog.products = [];  // reset list of products
		self.loadProducts(config);
	});

	// listen on events of type `shopCatalogFilter`
	$scope.$root.$on('shopCatalogFilter', function(event, filter) {
		var config;
		try {
			config = {params: filter};
		} catch (err) {
			config = null;
		}
		fetchURL = djangoShop.getLocationPath();
		$scope.catalog.products = [];  // reset list of products
		self.loadProducts(config);
	});

	$scope.catalog = {products: []};
	$scope.isLoading = false;
}]);


// Directive <ANY shop-catalog-list>
djangoShopModule.directive('shopCatalogList', function() {
	return {
		restrict: 'EAC',
		controller: 'CatalogListController'
	};
});

// Directive <ANY shop-sync-catalog="REST-API-endpoint">
// handle catalog list view combined with adding products to cart
djangoShopModule.directive('shopSyncCatalog', function() {
	return {
		restrict: 'A',
		controller: function() {},
		require: 'shopSyncCatalog',
		link: function(scope, element, attrs, controller) {
			if (!attrs.shopSyncCatalog)
				throw new Error("Directive shop-sync-catalog must point onto an URL");
			controller.syncCatalogUrl = attrs.shopSyncCatalog;
		}
	};
});


// Directive <ANY shop-sync-catalog="{id: {{ product.id }}, quantity: {{ product.quantity }} }">
// This directive must be a child of <ANY shop-sync-catalog...>. It synchronizes the local scope
// of a catalog item.
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
					prev_item = response;
					angular.extend($scope.catalog_item, response);
					$scope.$emit('shopUpdateCarticonCaption');
					isLoading = false;
				}).error(function(msg) {
					console.error('Unable to sync quantity: ' + msg);
					isLoading = false;
				});
			}

		}],
		link: function(scope, element, attrs, controllers) {
			if (!attrs.shopSyncCatalogItem)
				throw new Error("Directive shop-sync-catalog-item must provide an initialization object");
			controllers[1].parent = controllers[0];
			scope.catalog_item = scope.$eval(attrs.shopSyncCatalogItem);
		}
	};
});


})(window.angular);
