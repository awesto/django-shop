(function(angular, undefined) {
'use strict';

// module: django.shop, TODO: move this into a summary JS file
var djangoShopModule = angular.module('django.shop.order', []);

// Directive <shop-time>
// handle a djangoSHOP's timestamp
djangoShopModule.directive('shopTimestamp', ['$filter', '$locale', 'translation', function($filter, $locale, translation) {
	return {
		restrict: 'EAC',
		link: function(scope, element, attrs) {
			var timestamp = new Date(attrs.shopTimestamp);
			element.html($filter('date')(timestamp, attrs.timeFormat));
		}
	};
}]);

djangoShopModule.provider('translation', function() {
	var self = this;

	this.setDesignations = function(designators) {
		self.designators = designators;
	};

	this.$get = function() {
		return self;
	};
});

})(window.angular);
