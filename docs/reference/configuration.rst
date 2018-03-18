.. reference/configuration:

==========================
Configuration and Settings
==========================

The **django-SHOP** framework itself, requires only a few configuration directives. However, since
each e-commerce site built around **django-SHOP** consists of the merchant's own project, plus a
collection of third party Django apps, here is a summary of mandatory and some optional
configuration settings:


Django-SHOP specific settings
=============================

App Label
---------

This label is required internally to configure the name of the database tables used in the
merchant's implementation.

.. code-block:: python

	SHOP_APP_LABEL = 'myshop'

There is no default setting.


Site Framework
--------------

You should always activate Django's site framework and set a default for

.. code-block:: python

	SITE_ID = 1


Alternative User Model
----------------------

Django's built-in User model lacks a few features required by **django-SHOP**, mainly the
possibility to use the email address as the login credential. This overridden model is 100% field
compatible to Django's internal model and even reuses its own database table, namely ``auth_user``.

.. code-block:: python

	AUTH_USER_MODEL = 'email_auth.User'

Since this user model intentionally does not enforce uniqueness on the email address, Django would
complain if we do not silence this system check:

.. code-block:: python

	SILENCED_SYSTEM_CHECKS = ['auth.W004']

For further information, please refer to the :ref:`reference/customer-model` documentation.


Authentication Backends
-----------------------

.. code-block:: python

	AUTHENTICATION_BACKENDS = [
	    'django.contrib.auth.backends.ModelBackend',
	    'allauth.account.auth_backends.AuthenticationBackend',
	]

.. _allauth: http://django-allauth.readthedocs.io/en/latest/


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

Unless amounts never reach a thousand, it is advised to activate a separator for better readability.

.. code-block:: python

	USE_THOUSAND_SEPARATOR = True

Outside of the US, it generally is a good idea to activate localization for numeric types.

.. code-block:: python

	USE_L10N = True


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

	SHOP_CART_MODIFIERS = [
	    'shop.modifiers.defaults.DefaultCartModifier',
	    'shop.modifiers.taxes.CartExcludedTaxModifier',
	    # other modifiers
	]

For further information, please refer to the :ref:`reference/cart-modifiers` documentation.


Installed Django Applications
-----------------------------

This is a configuration known to work. Special and optional apps are discussed below.

.. code-block:: python

	INSTALLED_APPS = [
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
	]

* ``email_auth`` optional but recommended, overrides the built-in authentification. It must be
  located after ``django.contrib.auth``.
* ``polymorphic`` only required, if the site requires more than one type of product model.
  It presumes that django-polymorphic_ is installed.
* ``djangocms_text_ckeditor`` optionally adds a WYSIWYG HTML editor which integrates well with
  **django-CMS**.
* ``django_select2`` optionally adds a select field to Django's admin, with integrated
  autocompletion. Very useful for addings links to products manually. It presumes that
  django-select2_ is installed.
* ``cmsplugin_cascade`` adds the functionality to add CMS plugins, as provided by **django-SHOP**,
  to arbitrary CMS placeholders. This setting including submodules can be removed, if all templates
  are created manually.
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
  functionality to the **django-SHOP** framework.
* ``django_fsm`` and ``fsm_admin``, required, add the Finite State Machine to the **django-SHOP**
  framework.
* ``djng`` only required for installations using AngularJS, which is the recommended JavaScript
  framework. It adds the interface layer between Django and AngularJS and presumes that
  django-angular_ is installed.
* ``cms``, ``menus`` and ``treebeard`` are required if **django-SHOP** is used in combination with
  **djangoCMS**.
* ``compressor``, highly recommended. Concatenates and minifies CSS and JavaScript files on
  production systems. It presumes that django-compressor_ is installed.
* ``sekizai``, highly recommended, allows the template designer to group CSS and JavaScript
  file includes. It presumes that django-sekizai_ is installed.
* ``sass_processor``, optional but recommended, used to convert SASS into pure CSS together
  with debugging information. It presumes that django-sass-processor_ is installed.
* ``django_filters``, optionally used to filter products by their attributes using request
  parameters.
* ``filer``, highly recommended, manage your media files in Django. It presumes that django-filer_
  is installed.
* ``easy_thumbnails`` and ``easy_thumbnails.optimize``, highly recommended, handle thumbnail
  generation and optimization. It presumes that easy-thumbnails_ is installed.
* ``parler`` is an optional framework which handles the translation of models fields into other
  natural languages.
* ``post_office`` highly recommended. An asynchronous mail delivery application which does not
  interrupt the request-response cycle when sending mail.
* ``haystack`` optional, handles the interface between Django and Elasticsearch – a full-text
  search engine. It presumes a running and available instance of ElasticSearch and that
  django-haystack_ and drf-haystack_ is installed.
* ``shop`` the **django-SHOP** framework.
* ``my_shop_implementation`` replace this by the merchant's implementation of his shop.

.. _django-polymorphic: https://django-polymorphic.readthedocs.org/
.. _django-select2: https://django-select2.readthedocs.org/
.. _django-angular: https://django-angular.readthedocs.org/
.. _django-compressor: https://django-compressor.readthedocs.org/
.. _django-sekizai: https://django-sekizai.readthedocs.org/
.. _django-sass-processor: https://github.com/jrief/django-sass-processor/
.. _django-haystack: https://django-haystack.readthedocs.org/
.. _drf-haystack: https://drf-haystack.readthedocs.org/
.. _easy-thumbnails: https://easy-thumbnails.readthedocs.org/
.. _django-filer: https://django-filer.readthedocs.org/


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
	    'shop.middleware.MethodOverrideMiddleware',
	    'cms.middleware.language.LanguageCookieMiddleware',
	    'cms.middleware.user.CurrentUserMiddleware',
	    'cms.middleware.page.CurrentPageMiddleware',
	    'cms.middleware.toolbar.ToolbarMiddleware',
	)

* ``djng.middleware.AngularUrlMiddleware`` adds a special router, so that we can use Django's
  ``reverse`` function from inside JavaScript. Only required in conjunction with django-angular_.
* ``shop.middleware.CustomerMiddleware`` add the Customer object to each request.
* ``shop.middleware.MethodOverrideMiddleware`` transforms PUT requests wrapped as POST requests
  back into the PUT method. This is required for compatibility with some JS frameworks and proxies.


Static Files
------------

If ``compressor`` and/or ``sass_processor`` are part of ``INSTALLED_APPS``, add their finders to
the list of the default ``STATICFILES_FINDERS``:

.. code-block:: python

	STATICFILES_FINDERS = [
	    'django.contrib.staticfiles.finders.FileSystemFinder',
	    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	    'sass_processor.finders.CssFinder',
	    'compressor.finders.CompressorFinder',
	]


**Django-SHOP** requires a few third party packages, which are not available from PyPI, they
instead must be installed via ``npm install``. In order to make these files available to our Django
application, we use the configuration setting:

.. code-block:: python

	STATICFILES_DIRS = [
	    ('node_modules', '/path/to/project/node_modules'),
	]

Some files installed by ``npm`` are processed by django-sass-processor_ and hence their path
must be made available:

.. code-block:: python

	NODE_MODULES_URL = STATIC_URL + 'node_modules/'

	SASS_PROCESSOR_INCLUDE_DIRS = (
	    os.path.join(PROJECT_ROOT, 'node_modules'),
	)

* The string provided by ``NODE_MODULES_URL`` is used by the special function ``get-setting()``
  in the provided SASS files.
* ``SASS_PROCESSOR_INCLUDE_DIRS`` extends the list of folders to look for ``@import ...`` statements
  in the provided SASS files.


Template Context Processors
---------------------------

Templates rendered by the **django-SHOP** framework require some additional objects or configuration
settings. Add them to each template using these context processors:

.. code-block:: python

	TEMPLATES = [{
	    ...
	    'OPTIONS': {
	        'context_processors': (
	            ...
	            'shop.context_processors.customer',
	            'shop.context_processors.ng_model_options',
	        ),
	    },
	}]

``shop.context_processors.customer`` adds the Customer object to the rendering context.

``shop.context_processors.ng_model_options`` adds the :ref:`reference/configuration#angular-specific-settings`
to the rendering context.


Configure the Order Workflow
----------------------------

The ordering workflow can be configured using a list or tuple of mixin classes.

.. code-block:: python

	SHOP_ORDER_WORKFLOWS = (
	    'shop.payment.defaults.PayInAdvanceWorkflowMixin',
	    'shop.shipping.defaults.CommissionGoodsWorkflowMixin',
	    # other workflow mixins
	)

This prevents to display all transitions configured by the workflow mixins inside the administration
backend:

	FSM_ADMIN_FORCE_PERMIT = True


Email settings
--------------

Since **django-SHOP** communicates with its customers via email, having a working outgoing e-mail
service is a fundamental requirement for **django-SHOP**. Adopt these settings to your
configuration. Please remember that e-mail is sent asynchronously via django-post_office_.

.. code-block:: python

	EMAIL_HOST = 'smtp.example.com'
	EMAIL_PORT = 587
	EMAIL_HOST_USER = 'no-reply@example.com'
	EMAIL_HOST_PASSWORD = 'smtp-secret-password'
	EMAIL_USE_TLS = True
	DEFAULT_FROM_EMAIL = 'My Shop <no-reply@example.com>'
	EMAIL_REPLY_TO = 'info@example.com'
	EMAIL_BACKEND = 'post_office.EmailBackend'

.. _django-post_office: https://pypi.python.org/pypi/django-post_office


Session Handling
----------------

For performance reasons it is recommended to use a memory based session store such as Redis, rather
than a database or disk based store.

.. code-block:: python

	SESSION_ENGINE = 'redis_sessions.session'
	SESSION_SAVE_EVERY_REQUEST = True
	SESSION_REDIS_PREFIX = 'myshop-session'
	SESSION_REDIS_DB = 0


Caching Backend
---------------

For performance reasons it is recommended to use a memory based cache such as Redis, rather than a
disk based store. In comparison to memcached, Redis can invalidate cache entries using keys with
wildcards, which is a big advantage in **django-SHOP**.

.. code-block:: python

	CACHES = {
	    'default': {
	        'BACKEND': 'redis_cache.RedisCache',
	        'LOCATION': os.environ.get('REDIS_LOCATION', 'redis://localhost:6379/0'),
	        'KEY_PREFIX': 'myshop-cache',
	    },
	}

	CACHE_MIDDLEWARE_ALIAS = 'default'
	CACHE_MIDDLEWARE_SECONDS = 3600
	CACHE_MIDDLEWARE_KEY_PREFIX = 'myshop-cache'


Internationalisation Support
============================

Always localize decimal numbers unless you operate you site in the United States:

.. code-block:: python

	USE_L10N = True


These settings for internationalisation are known to work in combination with django-cms_ and
django-parler_.

.. code-block:: python

	USE_I18N = True

	LANGUAGE_CODE = 'en'

	LANGUAGES = [
	    ('en', "English"),
	    ('de', "Deutsch"),
	]

	PARLER_DEFAULT_LANGUAGE = 'en'

	PARLER_LANGUAGES = {
	    1: [
	        {'code': 'de'},
	        {'code': 'en'},
	    ],
	    'default': {
	        'fallbacks': ['de', 'en'],
	    },
	}

	CMS_LANGUAGES = {
	    'default': {
	        'fallbacks': ['en', 'de'],
	        'redirect_on_fallback': True,
	        'public': True,
	        'hide_untranslated': False,
	    },
	    1: [{
	        'public': True,
	        'code': 'en',
	        'hide_untranslated': False,
	        'name': 'English',
	        'redirect_on_fallback': True,
	    }, {
	        'public': True,
	        'code': 'de',
	        'hide_untranslated': False,
	        'name': 'Deutsch',
	        'redirect_on_fallback': True,
	    },]
	}

.. _django-cms: https://django-cms.readthedocs.io/
.. _django-parler: https://django-parler.readthedocs.io/


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

	SERIALIZATION_MODULES = {'json': 'shop.money.serializers'}

Since the client side is not allowed to do any price and quantity computations, Decimal values are
transferred to the client using strings. This also avoids nasty rounding errors.

.. code-block:: python

	COERCE_DECIMAL_TO_STRING = True


Django-CMS and Cascade settings
-------------------------------

**Django-SHOP** requires at least one CMS template. Assure that it contains a placeholder able to
accept

.. code-block:: python

	CMS_TEMPLATES = [
	    ('myshop/pages/default.html', _("Default Page")),
	]

	CMS_PERMISSION = False

	cascade_workarea_glossary = {
	    'breakpoints': ['xs', 'sm', 'md', 'lg'],
	    'container_max_widths': {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170},
	    'fluid': False,
	    'media_queries': {
	        'xs': ['(max-width: 768px)'],
	        'sm': ['(min-width: 768px)', '(max-width: 992px)'],
	        'md': ['(min-width: 992px)', '(max-width: 1200px)'],
	        'lg': ['(min-width: 1200px)'],
	    },
	}

	CMS_PLACEHOLDER_CONF = {
	    'Breadcrumb': {
	        'plugins': ['BreadcrumbPlugin'],
	        'parent_classes': {'BreadcrumbPlugin': None},
	        'glossary': cascade_workarea_glossary,
	    },
	    'Commodity Details': {
	        'plugins': ['BootstrapContainerPlugin', 'BootstrapJumbotronPlugin'],
	        'parent_classes': {
	            'BootstrapContainerPlugin': None,
	            'BootstrapJumbotronPlugin': None,
	        },
	        'glossary': cascade_workarea_glossary,
	    },
	    'Main Content': {
	        'plugins': ['BootstrapContainerPlugin', 'BootstrapJumbotronPlugin'],
	        'parent_classes': {
	            'BootstrapContainerPlugin': None,
	            'BootstrapJumbotronPlugin': None,
	            'TextLinkPlugin': ['TextPlugin', 'AcceptConditionPlugin'],
	        },
	        'glossary': cascade_workarea_glossary,
	    },
	    'Static Footer': {
	        'plugins': ['BootstrapContainerPlugin', ],
	        'parent_classes': {
	            'BootstrapContainerPlugin': None,
	        },
	        'glossary': cascade_workarea_glossary,
	    },
	}


**Django-SHOP** enriches **djangocms-cascade** with a few shop specific plugins.

.. code-block:: python

	from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig

	CMSPLUGIN_CASCADE_PLUGINS = [
	    'cmsplugin_cascade.segmentation',
	    'cmsplugin_cascade.generic',
	    'cmsplugin_cascade.icon',
	    'cmsplugin_cascade.link',
	    'shop.cascade',
	    'cmsplugin_cascade.bootstrap3',
	]

	CMSPLUGIN_CASCADE = {
	    'link_plugin_classes': [
	        'shop.cascade.plugin_base.CatalogLinkPluginBase',
	        'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
	        'shop.cascade.plugin_base.CatalogLinkForm',
	    ],
	    'alien_plugins': ['TextPlugin', 'TextLinkPlugin', 'AcceptConditionPlugin'],
	    'bootstrap3': {
	        'template_basedir': 'angular-ui',
	    },
	    'plugins_with_sharables': {
	        'BootstrapImagePlugin': ['image_shapes', 'image_width_responsive', 'image_width_fixed',
	                                 'image_height', 'resize_options'],
	        'BootstrapPicturePlugin': ['image_shapes', 'responsive_heights', 'image_size', 'resize_options'],
	    },
	    'bookmark_prefix': '/',
	    'segmentation_mixins': [
	        ('shop.cascade.segmentation.EmulateCustomerModelMixin', 'shop.cascade.segmentation.EmulateCustomerAdminMixin'),
	    ],
	    'allow_plugin_hiding': True,
	}


Since we want to add arbitrary links onto the detail view of a product, **django-SHOP** offers
a modified link plugin. This has to be enabled using the 3-tuple ``link_plugin_classes``.

**Django-SHOP** uses AngularJS rather than jQuery to control its dynamic HTML widgets.
We therefore have to override the default with this settings:
``CMSPLUGIN_CASCADE['bootstrap3']['template_basedir']``.

For a detailed explanation of these configuration settings, please refer to the documentation
of djangocms-cascade_.

.. _djangocms-cascade: http://djangocms-cascade.readthedocs.org


CK Text Editor settings
-----------------------

By default, **django-CMS** uses the CKEditor_ plugin which can be heavily configured. Settings which
have shown to be useful are:

.. code-block:: python

	CKEDITOR_SETTINGS_CAPTION = {
	    'language': '{{ language }}',
	    'skin': 'moono',
	    'height': 70,
	    'toolbar_HTMLField': [
	        ['Undo', 'Redo'],
	        ['Format', 'Styles'],
	        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
	        ['Source']
	    ],
	}

	CKEDITOR_SETTINGS_DESCRIPTION = {
	    'language': '{{ language }}',
	    'skin': 'moono',
	    'height': 250,
	    'toolbar_HTMLField': [
	        ['Undo', 'Redo'],
	        ['cmsplugins', '-', 'ShowBlocks'],
	        ['Format', 'Styles'],
	        ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
	        ['Maximize', ''],
	        '/',
	        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
	        ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
	        ['HorizontalRule'],
	        ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Table'],
	        ['Source']
	    ],
	}

.. _CKEditor: https://github.com/divio/djangocms-text-ckeditor


Media assets handling
---------------------

**Django-CMS** and **django-SHOP** rely on django-filer_ in combination with easy-thumbnails_ to
manage the media assets.

.. code-block:: python

	MEDIA_ROOT = '/path/to/project/media'

	MEDIA_URL = '/media/'

	FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True

	FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

	THUMBNAIL_OPTIMIZE_COMMAND = {
	    'gif': '/usr/bin/optipng {filename}',
	    'jpeg': '/usr/bin/jpegoptim {filename}',
	    'png': '/usr/bin/optipng {filename}'
	}

	THUMBNAIL_PRESERVE_EXTENSIONS = True

	THUMBNAIL_PROCESSORS = [
	    'easy_thumbnails.processors.colorspace',
	    'easy_thumbnails.processors.autocrop',
	    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
	    'easy_thumbnails.processors.filters',
	]

all settings are explained in detail in the documentation of django-filer_ and easy-thumbnails_.


Full Text Search
----------------

Presuming that you installed and run an ElasticSearchEngine_ server, configure Haystack:

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


.. _ElasticSearchEngine: https://www.elastic.co/products/elasticsearch

.. _reference/configuration#angular-specific-settings:

AngularJS specific settings
---------------------------

The cart's totals are updated after an input field has been changed. For usability reasons it makes
sense to `delay this`_, so that only after a certain time of inactivity, the update is triggered.

.. code-block:: python

	SHOP_ADD2CART_NG_MODEL_OPTIONS = "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}"

This configuration updates the cart after changing the quantity and 500 milliseconds of inactivity
or field blurring. It is used by the "Add to cart" form.

.. code-block:: python

	SHOP_EDITCART_NG_MODEL_OPTIONS = "{updateOn: 'default blur', debounce: {'default': 2500, 'blur': 0}}"

This configuration updates the cart after changing any of the product's quantities and 2.5 seconds
of inactivity or field blurring. It is used by the "Edit cart" form.

.. _delay this: https://docs.angularjs.org/api/ng/directive/ngModelOptions


Select2 specific settings
-------------------------

django-select2_ adds a configurable autocompletion field to the project.

Change the include path to a local directory, if you prefer to install the JavaScript dependencies
via ``npm`` instead of relying on a preconfigured CDN:

.. code-block:: python

	SELECT2_CSS = 'node_modules/select2/dist/css/select2.min.css'
	SELECT2_JS = 'node_modules/select2/dist/js/select2.min.js'
