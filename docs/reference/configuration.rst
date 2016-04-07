.. reference/configuration:

==========================
Configuration and Settings
==========================

The **djangoSHOP** framework itself, requires only a few configuration directives. However, since
each e-commerce site built around **djangoSHOP** consists of the merchant's own project, plus a
collection of third party Django apps, here is a summary of mandatory and some optional
configuration settings:


DjangoSHOP settings
===================

App Label
---------

This label is required internally to configure the name of the database tables of used in the
merchant's implementation.

.. code-block:: python

	SHOP_APP_LABEL = 'myshop'


Alternative User Model
----------------------

Django's built-in User model lacks a few features required by **djangoSHOP**, mainly the
possibility to use the email address as the login credential. This overridden model is 100% field
compatible to Django's internal model and even reuses the database table ``auth_user``.

.. code-block:: python

	AUTH_USER_MODEL = 'email_auth.User'

Since this user model intentionally does not enforce uniqueness on the email address, Django would
complain if we do not silence this system check:

.. code-block:: python

	SILENCED_SYSTEM_CHECKS = ('auth.W004')

For further information, please refer to the :ref:`reference/customer-model` documentation.


Authentication Backends
-----------------------

.. code-block:: python

	AUTHENTICATION_BACKENDS = (
	    'django.contrib.auth.backends.ModelBackend',
	    'allauth.account.auth_backends.AuthenticationBackend',
	)


Currency
--------

Unless Money types are specified explicitly, each project requires a default currency:

.. code-block:: python

	SHOP_DEFAULT_CURRENCY = 'EUR'

The typical format to render an amount is ``$ 1.23``, but some merchant may prefer ``1.23 USD``.
By using the configuration setting:

.. code-block:: python

	SHOP_MONEY_FORMAT = '{symbol} {amount}'

we my specify our own money rendering format, where ``{symbol}`` is €, $, £, etc. and ``{currency}``
is EUR, USD, GBP, etc.


Cart Modifiers
--------------

Each project requires at least one cart modifier in order to initialize the cart. In most
implementations :class:`shop.modifiers.defaults.DefaultCartModifier` is enough, but depending
on the product models, the merchant's may implement an alternative.

To identify the taxes in the cart, use one of the provided tax modifiers or implement a customized
one.

Other modifiers may add extra payment and shipping costs, or rebate the total amount depending
on whatever appropriate.

.. code-block:: python

	SHOP_CART_MODIFIERS = (
	    'shop.modifiers.defaults.DefaultCartModifier',
	    'shop.modifiers.taxes.CartExcludedTaxModifier',
	    # other modifiers
	)

For further information, please refer to the :ref:`reference/cart-modifiers` documentation.


Installed Django Applications
-----------------------------

This is a configuration known to work. Special and optional apps are discussed below.

.. code-block:: python

	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'email_auth',
	    'polymorphic',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'djangocms_admin_style',
	    'django.contrib.admin',
	    'django.contrib.staticfiles',
	    'django.contrib.sitemaps',
	    'djangocms_text_ckeditor',
	    'django_select2',
	    'cmsplugin_cascade',
	    'cmsplugin_cascade.clipboard',
	    'cmsplugin_cascade.sharable',
	    'cmsplugin_cascade.extra_fields',
	    'cmsplugin_cascade.segmentation',
	    'cms_bootstrap3',
	    'adminsortable2',
	    'rest_framework',
	    'rest_framework.authtoken',
	    'rest_auth',
	    'django_fsm',
	    'fsm_admin',
	    'djng',
	    'cms',
	    'menus',
	    'treebeard',
	    'compressor',
	    'sekizai',
	    'sass_processor',
	    'django_filters',
	    'filer',
	    'easy_thumbnails',
	    'easy_thumbnails.optimize',
	    'parler',
	    'post_office',
	    'haystack',
	    'shop',
	    'my_shop_implementation',
	)

* ``email_auth`` optional but recommended, overrides the built-in authentification. It must be
  located after ``django.contrib.auth``.
* ``polymorphic`` required only, if the site requires more than one type of product model.
* ``djangocms_text_ckeditor`` optionally adds a WYSIWYG HTML editor which integrates well with
  **djangoCMS**.
* ``django_select2`` optionally adds a select field to Django's admin, with integrated
  autocompletion. Very useful for added links to products manually.
* ``cmsplugin_cascade`` adds the functionality to add CMS plugins, as provided by **djangoSHOP**,
  to arbitrary CMS placeholders.
* ``cmsplugin_cascade.clipboard`` allows the site administrator to copy a set of plugins in one
  installation and paste it into the placeholder of another one.
* ``cmsplugin_cascade.sharable`` allows the site administrator to share a preconfigurable set
  of plugin attributes into an alias, to be reused by many plugins of the same type.
* ``cmsplugin_cascade.extra_fields`` allows the site administrator to add arbitrary CSS classes,
  styles and ID-fields to entitled plugins.
* ``cmsplugin_cascade.segmentation`` allows to segment a set of plugins into logical units.
* ``cms_bootstrap3`` adds some templates and templatetags to render Bootstrap 3 styled menus
  and navigation bars.
* ``adminsortable2`` allows the site administrator to sort various items in Django's administration
  backend.
* ``rest_framework``, ``rest_framework.authtoken`` and ``rest_auth``, required, add the REST
  functionality to the **djangoSHOP** framework.
* ``django_fsm`` and ``fsm_admin``, required, add the Finite State Machine to the **djangoSHOP**
  framework.
* ``djng`` required for installations using AngularJS. Adds the interface layer between Django and
  AngularJS.
* ``cms``, ``menus`` and ``treebeard`` are required if **djangoSHOP** is used in combination with
  **djangoCMS**.
* ``compressor``, highly recommended, concatenates and minifies CSS and JavaScript files on
  production systems.
* ``sekizai``, highly recommended, allows the template designer to group CSS and JavaScript
  includes.
* ``sass_processor``, optional but recommended, used to convert SASS into pure CSS.
* ``django_filters``, optionally used to filter products by their attributes using request
  parameters.
* ``filer``, highly recommended, manage your media files in Django.
* ``easy_thumbnails`` and ``easy_thumbnails.optimize``, highly recommended, handle thumbnail
  generation and optimization.
* ``parler`` is an optional framework which handles the translation of models fields into other
  natural languages.
* ``post_office`` is an asynchronous mail delivery application.
* ``haystack`` handles the interface between Django and Elasticsearch – a full-text search engine.
* ``shop`` this framework.
* ``my_shop_implementation`` replace this by the merchant's implementation of his shop.


Middleware Classes
------------------

This is a configuration known to work. Special middleware classes are discussed below.

.. code-block:: python

	MIDDLEWARE_CLASSES = (
	    'djng.middleware.AngularUrlMiddleware',
	    'django.contrib.sessions.middleware.SessionMiddleware',
	    'django.middleware.csrf.CsrfViewMiddleware',
	    'django.contrib.auth.middleware.AuthenticationMiddleware',
	    'shop.middleware.CustomerMiddleware',
	    'django.contrib.messages.middleware.MessageMiddleware',
	    'django.middleware.locale.LocaleMiddleware',
	    'django.middleware.common.CommonMiddleware',
	    'django.middleware.gzip.GZipMiddleware',
	    'cms.middleware.language.LanguageCookieMiddleware',
	    'cms.middleware.user.CurrentUserMiddleware',
	    'cms.middleware.page.CurrentPageMiddleware',
	    'cms.middleware.toolbar.ToolbarMiddleware',
	)
	
	* ``djng.middleware.AngularUrlMiddleware`` adds a special router, so that we can use Django's
	  ``reverse`` function from inside JavaScript.
	* ``shop.middleware.CustomerMiddleware`` add the Customer object to each request.


Static Files
------------

If ``compressor`` and/or ``sass_processor`` are part of ``INSTALLED_APPS``, add their finders to
the list of the default ``STATICFILES_FINDERS``:

.. code-block:: python

	STATICFILES_FINDERS = (
	    'django.contrib.staticfiles.finders.FileSystemFinder',
	    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	    'sass_processor.finders.CssFinder',
	    'compressor.finders.CompressorFinder',
	)


Since **djangoSHOP** requires third party packages outside of PyPI and installed via
``bower install`` and ``npm install``, these files must be made available to Django through the
configuration setting:

.. code-block:: python

	STATICFILES_DIRS = (
	    os.path.join(BASE_DIR, 'static'),
	    ('bower_components', os.path.join(PROJECT_ROOT, 'bower_components')),
	    ('node_modules', os.path.join(PROJECT_ROOT, 'node_modules')),
	)

Some files installed by ``npm`` are processed by **django-sass-processor** and hence their path
must be made available:

.. code-block:: python

	NODE_MODULES_URL = STATIC_URL + 'node_modules/'
	
	SASS_PROCESSOR_INCLUDE_DIRS = (
	    os.path.join(PROJECT_ROOT, 'node_modules'),
	)


Template Context Processors
---------------------------

Templates rendered by the **djangoSHOP** framework require the Customer object in their context.
Configure this by adding a special template context processor:

.. code-block:: python

	TEMPLATES = [{
	    ...
	    'OPTIONS': {
	        'context_processors': (
	            ...
	            'shop.context_processors.customer',
	            'shop.context_processors.version',
	        ),
	    },
	}]


Workflow Mixins
---------------

.. code-block:: python

	SHOP_ORDER_WORKFLOWS = (
	    'shop.payment.defaults.PayInAdvanceWorkflowMixin',
	    'shop.shipping.defaults.CommissionGoodsWorkflowMixin',
	    # other workflow mixins
	)


REST Framework
--------------

The REST framework requires special settings. We namely must inform it how to serialize our special
Money type:

.. code-block:: python

	REST_FRAMEWORK = {
	    'DEFAULT_RENDERER_CLASSES': (
	        'shop.rest.money.JSONRenderer',
	        'rest_framework.renderers.BrowsableAPIRenderer',
	    ),
	    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
	    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
	    'PAGE_SIZE': 12,
	}
	
	SERIALIZATION_MODULES = {'json': str('shop.money.serializers')}


Django CMS and Cascade settings
-------------------------------

**DjangoSHOP** requires at least one CMS template. Assure that it contains a placeholder able to
accept 

.. code-block:: python

	CMS_TEMPLATES = (
	    ('myshop/pages/default.html', _("Default Page")),
	)

	CMS_PERMISSION = False


**DjangoSHOP** requires a few shop specific plugins for **djangocms-cascade**. Additionally we
gain some functionality to add links from CMS pages to products.

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.segmentation', 'cmsplugin_cascade.generic',
	    'cmsplugin_cascade.link', 'shop.cascade', 'cmsplugin_cascade.bootstrap3',)
	
	CMSPLUGIN_CASCADE = {
	    'dependencies': {
	        'shop/js/admin/shoplinkplugin.js': 'cascade/js/admin/linkpluginbase.js',
	    },
	    'alien_plugins': ('TextPlugin', 'TextLinkPlugin',),
	    'bootstrap3': {
	        'template_basedir': 'angular-ui',
	    },
	    'plugins_with_extra_fields': (
	        'BootstrapButtonPlugin',
	        'BootstrapRowPlugin',
	        'SimpleWrapperPlugin',
	        'HorizontalRulePlugin',
	        'ExtraAnnotationFormPlugin',
	        'ShopProceedButton',
	    ),
	    'segmentation_mixins': (
	        ('shop.cascade.segmentation.EmulateCustomerModelMixin', 'shop.cascade.segmentation.EmulateCustomerAdminMixin'),
	    ),
	}
	
	CMSPLUGIN_CASCADE_LINKPLUGIN_CLASSES = (
	    'shop.cascade.plugin_base.CatalogLinkPluginBase',
	    'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
	    'shop.cascade.plugin_base.CatalogLinkForm',
	)


Full Text Search
----------------

Presuming that you installed and run an ElasticSearchEngine server, configure Haystack:

.. code-block:: python

	HAYSTACK_CONNECTIONS = {
	    'default': {
	        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
	        'URL': 'http://localhost:9200/',
	        'INDEX_NAME': 'my_prefix-en',
	    },
	}

If you want to index other natural language, say German, add another prefix:

.. code-block:: python

	HAYSTACK_CONNECTIONS = {
	    ...
	    'de': {
	        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
	        'URL': 'http://localhost:9200/',
	        'INDEX_NAME': 'my_prefix-de',
	    }
	}
	HAYSTACK_ROUTERS = ('shop.search.routers.LanguageRouter',)


Various other settings
----------------------

For usability reasons it makes sense to update the cart's total upon change only after a certain
time of inactivity. This configuration sets this to 2500 milliseconds:

.. code-block:: python

	SHOP_EDITCART_NG_MODEL_OPTIONS = "{updateOn: 'default blur', debounce: {'default': 2500, 'blur': 0}}"

Change the include path to a local directory, if you don't want to rely on a CDN:

.. code-block:: python

	SELECT2_CSS = 'bower_components/select2/dist/css/select2.min.css'
	SELECT2_JS = 'bower_components/select2/dist/js/select2.min.js'

Since the client side is not allowed to do any price and quantity computations, Decimal values are
transferred to the client using strings. This also avoids nasty rounding errors.

.. code-block:: python

	COERCE_DECIMAL_TO_STRING = True

Prevent to display all transitions configured by the workflow mixins inside the administration
backend:

	FSM_ADMIN_FORCE_PERMIT = True
