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
	return {
		link: function(scope, element, attrs) {
			scope.proceedWithConversion = function(action) {
				angular.extend(window, googleReportConversion.vars);
				var opt = new Object();
				opt.onload_callback = function() {
					debugger;
					scope.proceedWith(action);
				}
				var conv_handler = window['google_trackConversion'];
				if (typeof(conv_handler) == 'function') {
					debugger;
					conv_handler(opt);
				}
			};
		}
	};
}]);


})(window.angular);
