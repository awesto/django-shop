(function(angular, undefined) {
'use strict';

var module = angular.module('myshop.navbar', []);

// Directive <ANY navbar-extra-top> hides the extra bar inside the main navigation bar
// when scrolled downwards.
module.directive('navbarExtraTop', ['$document', function($document) {
	return {
		restrict: 'EAC',
		link: function(scope, element, attrs) {
			var body = $document.find('body');
			var height = element[0].offsetHeight;

			$document.on('scroll', function(evt) {
				var offset = body[0].scrollTop / 2;
				offset = - Math.min(offset, height);
				element.css('margin-top', offset + 'px');
			});
		}
	};
}]);

})(window.angular);
