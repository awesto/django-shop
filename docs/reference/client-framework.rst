.. _reference/client-framework:

=====================
Client Side Framework
=====================

While Django doesn't impose any client side framework, **djangoSHOP** has to. Here we have to
consider that it is unrealistic to expect an e-commerce side, without any client-side operations.
For instance, during checkout the customer must be able to edit the cart interactively. We also
might want to offer autocompletion and infinite scroll.

Therefore the author of **djangoSHOP** has decided to add some reusable Javascript code to this
framework. The most obvious choice would have been jQuery since it is already used by the Django
administration backend. However by using jQuery, web designers adopting the templates for their
**djangoSHOP** implementation would inevitably have to adopt Javascript code. In order to prevent
this from happening, another popular Javascript framework was chosen: AngularJS_.

This means that template designers only have to add special HTML directives as provided by the
framework. They do not have to write or adopt any Javascript code, except for the initialization.

..note:: Since **djangoSHOP** uses REST for every part of the communication, the client side
	framework can be replaced by whatever appropriate.


Initialize the Application
==========================

As with any application, also the client side must be initialized. This in AngularJS is done
straight forward. Change the outermost HTML element, which typically is the ``<html>`` tag, to

.. code-block:: html

	<html ng-app="myShop">

somewhere in this file, include the Javascript files required by Angular.

For a better organization of the inluded files, it is strongly recommended to use django-sekizai_
as assets manager:

.. code-block:: django

	{% load static sekizai_tags %}
	
	{% addtoblock "js" %}<script src="{% static 'bower_components/picturefill/dist/picturefill.min.js' %}" type="text/javascript"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'bower_components/angular/angular.min.js' %}" type="text/javascript"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'bower_components/angular-sanitize/angular-sanitize.min.js' %}"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'bower_components/angular-i18n/angular-locale_de.js' %}"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'bower_components/angular-animate/angular-animate.min.js' %}"></script>{% endaddtoblock %}
	{% addtoblock "js" %}<script src="{% static 'bower_components/angular-messages/angular-messages.min.js' %}"></script>{% endaddtoblock %}

Before the closing ``</body>``-tag, we then combine those includes and initialize the client side
application. Say we declare a base template for our project:

.. code-block:: django
	:caption: myshop/pages/base.html

	{% load djng_tags %}
	<body>
	...
	{% render_block "js" postprocessor "compressor.contrib.sekizai.compress" %}
	<script type="text/javascript">
	angular.module('myShop', ['ngAnimate', 'ngMessages', 'ngSanitize',
		{% render_block "shop-ng-requires" postprocessor "shop.sekizai_processors.module_list" %}
	]).config(['$httpProvider', function($httpProvider) {
		$httpProvider.defaults.headers.common['X-CSRFToken'] = '{% csrf_value %}';
		$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	}]).config(['$locationProvider', function($locationProvider) {
		$locationProvider.html5Mode(false);
	}]){% render_block "shop-ng-config" postprocessor "shop.sekizai_processors.module_config" %};
	</script>
	
	</body>

By using Sekizai's templatetag ``render_block`` inside the initialization and configuration phase
of our Angular application, we can delegate the dependency resolution to template expansion and
inclusion.

For example, the editable cart requires its own Angular module, found in a separate Javascript file.
Since we honor the principle of encapsulation, we only want to include and initialize that module
if the customer loads the view to alter the cart. Here the template for our editable cart starts
with:

.. code-block:: django
	:caption: shop/cart/editable.html

	{% load static sekizai_tags %}
	
	{% addtoblock "js" %}<script src="{% static 'shop/js/cart.js' %}" type="text/javascript"></script>{% endaddtoblock %}
	{% addtoblock "shop-ng-requires" %}django.shop.cart{% endaddtoblock %}

Sekizai then collects the content between these ``addtoblock``s, and renders them using the
``render_block`` statements shown above. This concept allows us to delegate dependency resolution
and module initialization to whom it concerns.


Angular Modules
===============

The **djangoSHOP** framework declares a bunch of Angular directives and controllers, grouped into
separate modules. All these modules are placed into their own Javascript file and use the same
but unique naming scheme, for example ``django.shop.auth``, ``django.shop.cart``,
``django.shop.catalog`` etc., to avoid conflicts with other third party modules.



.. _AngularJS: https://www.angularjs.org/
.. _django-sekizai: 
