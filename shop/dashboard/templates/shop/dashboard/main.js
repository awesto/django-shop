{% load i18n %}
(function(angular, undefined) {
'use strict';

var djangoShopDashboard = angular.module('djangoShopDashboard');

djangoShopDashboard.config(['RestangularProvider', function(RestangularProvider) {
	RestangularProvider.addFullRequestInterceptor(function(element, operation, what, url, headers, params) {
		if (operation == "getList") {
		}
		return {params: params};
	});

	RestangularProvider.addResponseInterceptor(function(data, operation, what, url, response, deferred) {
		if (operation == "getList") {
			response.totalCount = data.count;
			return data.results;
		}
		return data;
	});

}]);

djangoShopDashboard.config(['NgAdminConfigurationProvider', function(nga) {
	var admin = nga.application("Dashboard");

	admin.baseApiUrl("{% url 'dashboard:root' %}");

	{% for name, viewset in dashboard_entities.items %}
	(function() {
		var entity = nga.entity("{{ name }}");

		entity.listView().fields([{% for field in viewset.list_fields %}
			{{ field }}{% if not forloop.last %},{% endif %}{% endfor %}
		]);

		entity.creationView().fields([{% for field in viewset.creation_fields %}
			{{ field }}{% if not forloop.last %},{% endif %}{% endfor %}
		]);

		entity.editionView().fields([{% for field in viewset.edition_fields %}
			{{ field }}{% if not forloop.last %},{% endif %}{% endfor %}
		]).onSubmitError(['error', 'entity', 'form', 'progression', 'notification',
		function(error, entity, form, progression, notification) {
			angular.forEach(error.data, function(value, field_name) {
				if (form[field_name]) {
					form[field_name].$setValidity(false);
				}
			});
			progression.done();
			notification.log("{% trans 'Some values are invalid, see details in the form' %}", { addnCls: 'humane-flatty-error' });
			return false;
		}]);
		admin.addEntity(entity);
	})();
	{% endfor %}

	nga.configure(admin);
}]);

})(window.angular);
