(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.utils', []);

// Directive <shop-time>
// handle a djangoSHOP's timestamp
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

	this.setTranslations = function(translations) {
		self.translations = translations;
	};

	this.$get = function() {
		return self;
	};
});

})(window.angular);
