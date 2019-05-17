(function(angular, undefined) {
'use strict';

var djangoShopModule = angular.module('django.shop.messages', []);


djangoShopModule.provider('djangoMessages', function() {
	var endpointURL;

	this.alertLevelMap = {
		'debug': 'bg-secondary text-white',
		'info': 'bg-info text-white',
		'success': 'bg-success text-white',
		'warning': 'bg-warning text-dark',
		'error': 'bg-danger text-white',
	};
	this.alertIconMap = {
		'debug': 'fa-bug',
		'info': 'fa-info-circle',
		'success': 'fa-check-circle',
		'warning': 'fa-exclamation-circle',
		'error': 'fa-exclamation-triangle',
	};

	this.setEndpoint = function(url) {
		endpointURL = url;
	};

	this.$get = ['$http', '$rootScope', '$timeout', function($http, $rootScope, $timeout) {
		var self = this;
		$rootScope.$on('shop.messages.fetch', fetchNewMessages);
		$timeout(function() {
			fetchNewMessages();
		});

		function fetchNewMessages() {
			$http.get(endpointURL).then(function(response) {
				$rootScope.djangoMessages = angular.isArray($rootScope.djangoMessages) ? $rootScope.djangoMessages : [];
				angular.extend($rootScope.djangoMessages, response.data.django_messages);
				angular.forEach($rootScope.djangoMessages, function(message) {
					if (message.delay > 0 && angular.isUndefined(message.timeout)) {
						message.timeout = $timeout(function() {
							self.removeMessage(message);
						}, message.delay);
					}
				});
			});
		}

		this.removeMessage = function(message) {
			message.hide = true;
			$timeout(function() {
				var index = $rootScope.djangoMessages.indexOf(message);
				if (index >= 0) {
					$rootScope.djangoMessages.splice(index, 1);
				}
			}, 250);
		};

		return this;
	}];
});


djangoShopModule.directive('shopToastMessages', ['$rootScope', 'djangoMessages', function($rootScope, djangoMessages) {
	return {
		restrict: 'E',
		scope: true,
		templateUrl: 'shop/toast-messages.html',
		link: function(scope, element, attrs) {
			scope.alertLevel = function(message) {
				return djangoMessages.alertLevelMap[message.level] || 'text-dark';
			};
			scope.alertIcon = function(message) {
				return djangoMessages.alertIconMap[message.level] || 'fa-circle-o';
			};
			scope.appear = function(message) {
				if (!message.hide) {
					return 'show';
				}
			};
			scope.close = djangoMessages.removeMessage;
		}
	};
}]);


/*
djangoShopModule.directive('toast', ['$timeout', function($timeout) {
	return {
		restrict: 'C',
		scope: true,
		link: function(scope, element, attrs) {
			$timeout(function() {
				element.addClass('show');
			}, 500);
			scope.close = function() {
				element.removeClass('show');
				$timeout(function() {
					element.addClass('hide');
				}, 500);
			};
			scope.alertLevel = function(levelTag) {
				switch (levelTag) {
					case 'debug': return 'bg-secondary text-white';
					case 'info': return 'bg-info text-white';
					case 'success': return 'bg-success text-white';
					case 'warning': return 'bg-warning text-dark';
					case 'error': return 'bg-danger text-white';
					default: return 'text-dark';
				}
			};
			scope.alertIcon = function(levelTag) {
				switch (levelTag) {
					case 'debug': return 'fa-bug';
					case 'info': return 'fa-info-circle';
					case 'success': return 'fa-check-circle';
					case 'warning': return 'fa-exclamation-circle';
					case 'error': return 'fa-exclamation-triangle';
					default: return 'fa-circle-o';
				}
			};
			if (parseInt(attrs.delay)) {
				$timeout(scope.close, attrs.delay);
			}
		}
	};
}]);
*/

})(window.angular);
