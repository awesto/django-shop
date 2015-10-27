(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.google_analytics', []);

djangoShopModule.provider('googleReportConversion', function() {
	var self = this;
	self.vars = {google_conversion_format: "3"};

	this.setSnippetVars = function(vars) {
		angular.extend(self.vars, vars);
	};

	this.$get = function() {
		return self;
	};
});

djangoShopModule.directive('shopDialogProceed', ['googleReportConversion', function(googleReportConversion) {
	var conv_handler = window['google_trackConversion'];

	return {
		link: function(scope, element, attrs) {
			scope.proceedWithConversion = function(action) {
				var opt = {
					onload_callback: function() {
						scope.proceedWith(action);
					}
				};
				angular.extend(window, googleReportConversion.vars);
				if (angular.isFunction(conv_handler)) {
					conv_handler(opt);
				}
			};
		}
	};
}]);


})(window.angular);
