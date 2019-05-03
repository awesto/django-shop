(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.utils', []);

// Directive <shop-time>
// handle a django-SHOP's timestamp
djangoShopModule.directive('shopTimestamp', ['$filter', '$locale', function($filter, $locale) {
	return {
		restrict: 'EAC',
		link: function(scope, element, attrs) {
			var timestamp = new Date(attrs.shopTimestamp);
			element.html($filter('date')(timestamp, attrs.timeFormat));
		}
	};
}]);


djangoShopModule.provider('djangoShop', function() {
	var self = this;

	this.getLocationPath = function() {
		return self.location.pathname;
	};

	// Build a `params` object using the current search query string
	// Optionally provide a list of keys, if you are interested into a subset of parameters
	this.paramsFromSearchQuery = function() {
		var args = Array.prototype.slice.call(arguments), params = {}, i, queries, pair;
		queries = self.location.search.substring(self.location.search.indexOf('?') + 1).split('&');
		for (i = 0; i < queries.length; i++) {
			pair = queries[i].split('=');
			if (pair.length === 2 && (args.length === 0 || args.indexOf(pair[0]) >= 0)) {
				params[pair[0]] = decodeURIComponent(pair[1]);
			}
		}
		return params;
	};

	this.$get = ['$window', function($window) {
		self.location = $window.location;
		return self;
	}];

});


// Used as filter to create a list of integers for iteration by ``ng-repeat`` and similar.
// Usage: ``<div ng-repeat="x in some_value|range:1" ng-bind="x"></div>``
// If ``some_value`` is 3, then the above is rendered as ``<div>1</div><div>2</div><div>3</div>``.
djangoShopModule.filter('range', function() {
	return function(end, start) {
		var direction, result = [];
		if (angular.isNumber(end)) {
			start = angular.isNumber(start) ? start : 0;
			direction = (start <= end) ? 1 : -1;
			while (start !== end + direction) {
				result.push(start);
				start += direction;
			}
		}
		return result;
	};
});


})(window.angular);
