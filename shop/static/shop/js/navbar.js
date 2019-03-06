(function(angular, undefined) {
'use strict';

var module = angular.module('django.shop.navbar', ['django.cms.bootstrap']);

// Directive <nav ...> watching for scroll events. In case the user scrolled below a certain
// threshold, two CSS classes are added to this element: Either "scrolled scrolled-down", when
// the user scrolled down, or "scrolled scrolled-up" when the user scrolled up.
module.directive('nav', ['$document', '$window', function($document, $window) {
	return {
		restrict: 'E',
		link: function(scope, element, attrs) {
			var prevScrollY = $window.scrollY;
			var threshold = Number(attrs['scrollThreshold']) || 32;

			function scrollHandler(evt) {
				if ($window.scrollY < threshold) {
					element.removeClass('scrolled scrolled-down scrolled-up');
				} else {
					element.addClass('scrolled');
					if ($window.scrollY < prevScrollY) {
						element.removeClass('scrolled-down');
						element.addClass('scrolled-up');
					} else if ($window.scrollY > prevScrollY) {
						element.removeClass('scrolled-up');
						element.addClass('scrolled-down');
					}
				}
				prevScrollY = $window.scrollY;
			}

			$document.on('scroll', scrollHandler);
			scrollHandler();
		}
	};
}]);

})(window.angular);
