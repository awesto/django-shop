(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.catalog', ['ui.bootstrap', 'djng.forms', 'django.shop.utils']);


djangoShopModule.controller('ModalInstanceCtrl',
                            ['$scope', '$http', '$uibModalInstance', 'context',
                            function($scope, $http, $uibModalInstance, context) {
	$scope.proceed = function(url) {
		$uibModalInstance.close({url: url});
	};

	$scope.cancel = function() {
		$uibModalInstance.dismiss('cancel');
	};

	$scope.context = context;
}]);


// Directive <ANY shop-add-to-cart="REST-API-endpoint">
// handle dialog box on the product's detail page to add a product to the cart or watch-list
djangoShopModule.directive('shopAddToCart', ['$http', '$log', function($http, $log) {
	return {
		controller: angular.noop,
		restrict: 'EA',
		require: 'shopAddToCart',
		scope: true,
		link: function(scope, element, attrs) {
			if (!attrs.shopAddToCart)
				throw new Error("Directive shop-add-to-cart must point onto an URL");

			// load initial context
			$http.get(attrs.shopAddToCart).then(function(response) {
				scope.context = response.data;
			}).catch(function(ressponse) {
				$log.error('Unable to get context: ' + ressponse.statusText);
			});

			scope.updateContext = function() {
				$http.post(attrs.shopAddToCart, scope.context).then(function(response) {
					scope.context = response.data;
				}).catch(function(response) {
					$log.error('Unable to update context: ' + response.statusText);
				});
			};
		}
	};
}]);


djangoShopModule.directive('button',
                           ['$http', '$log', '$q', '$rootScope', '$uibModal', '$window', 'djangoForm',
                           function($http, $log, $q, $rootScope, $uibModal, $window, djangoForm) {
	return {
		restrict: 'E',
		require: '^?shopAddToCart',
		scope: true,
		link: function (scope, element, attrs, controller) {
			if (!controller)
				return;

			// prefix functions openModal/addToCart/redirectTo with: do(...).then(...)
			// to create the initial promise
			scope.do = function(resolve, reject) {
				return $q.resolve().then(resolve, reject);
			};

			scope.openModal = function(modalTitle) {
				return function() {
					scope.context.modalTitle = modalTitle;
					return $uibModal.open({
						templateUrl: 'AddToCartModalDialog.html',
						controller: 'ModalInstanceCtrl',
						resolve: {
							context: function() {
								return scope.context;
							}
						}
					}).result;
				};
			};

			scope.addToCart = function(endpoint) {
				return function(context) {
					var deferred = $q.defer();
					$http.post(endpoint, scope.context).then(function(response) {
						scope.context.is_in_cart = true;
						deferred.resolve(context);
					}).catch(function(response) {
						$log.error('Unable to update context: ' + response.statusText);
						deferred.reject();
					});
					return deferred.promise;
				};
			};

			scope.emit = function(event) {
				return function(response) {
					$rootScope.$emit(event);
					return $q.resolve(response);
				};
			};

			scope.redirectTo = function(url) {
				return function(response) {
					if (angular.isDefined(response.url)) {
						$window.location.assign(response.url);
					} else if (angular.isDefined(url)) {
						$window.location.assign(url);
					}
				};
			};
		}
	};
}]);


djangoShopModule.controller('CatalogListController', ['$log', '$scope', '$http', 'djangoShop',
                                             function($log, $scope, $http, djangoShop) {
	var self = this, fetchURL = null;

	this.loadProducts = function(config) {
		if ($scope.isLoading || fetchURL === null)
			return;
		$scope.isLoading = true;
		$http.get(fetchURL, config).then(function(response) {
			fetchURL = response.data.next;
			$scope.catalog.count = response.data.count;
			$scope.catalog.products = $scope.catalog.products.concat(response.data.results);
		}).catch(function() {
			fetchURL = null;
		}).finally(function() {
			$scope.isLoading = false;
		});
	};

	this.resetProductsList = function() {
		fetchURL = djangoShop.getLocationPath();
		$scope.catalog.products = [];
	};

	$scope.loadMore = function() {
		var config = {params: djangoShop.paramsFromSearchQuery.apply(this, arguments)};
		$log.log('load more products ...');
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
		restrict: 'EA',
		controller: 'CatalogListController',
		link: function(scope, element, attrs, controller) {
			var infiniteScroll = scope.$eval(attrs.infiniteScroll);

			scope.$root.$on('shop.catalog.search', function(event, params) {
				if (infiniteScroll) {
					controller.resetProductsList();
					controller.loadProducts({params: params});
				} else {
					$window.location.reload();
				}
			});

			scope.$root.$on('shop.catalog.filter', function(event, params) {
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
		controller: ['$http', '$log', '$rootScope', '$scope', function($http, $log, $rootScope, $scope) {
			var self = this, prev_item = null, isLoading = false;

			$scope.syncQuantity = function() {
				if (isLoading || angular.equals($scope.catalog_item, prev_item))
					return;
				isLoading = true;
				$http.post(self.parent.syncCatalogUrl, $scope.catalog_item).then(function(response) {
					var cart = response.data.cart;
					delete response.data.cart;
					prev_item = response.data;
					angular.extend($scope.catalog_item, response.data);
					$rootScope.$broadcast('shop.cart.change');
					isLoading = false;
				}).catch(function(response) {
					$log.error('Unable to sync quantity: ' + response.statusText);
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
