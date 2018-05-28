# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Django settings for myshop project.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy

from cmsplugin_cascade.utils import format_lazy

import six

SHOP_APP_LABEL = 'myshop'
BASE_DIR = os.path.dirname(__file__)

SHOP_TUTORIAL = os.environ.get('DJANGO_SHOP_TUTORIAL')
if SHOP_TUTORIAL is None:
    raise ImproperlyConfigured("Environment variable DJANGO_SHOP_TUTORIAL is not set")
if SHOP_TUTORIAL not in ['commodity', 'i18n_commodity', 'smartcard', 'i18n_smartcard',
                         'i18n_polymorphic', 'polymorphic']:
    msg = "Environment variable DJANGO_SHOP_TUTORIAL has an invalid value `{}`"
    raise ImproperlyConfigured(msg.format(SHOP_TUTORIAL))

# Root directory for this django project
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir))

# Directory where working files, such as media and databases are kept
WORK_DIR = os.environ.get('DJANGO_WORKDIR', os.path.abspath(os.path.join(PROJECT_ROOT, os.path.pardir, 'workdir')))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

ADMINS = (("The Merchant", 'the.merchant@example.com'),)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nqniwbt=%@5a(e8%&h#c^0()64(ujs0=4%_nyajn*t6a$ca&at'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DJANGO_DEBUG'))

ALLOWED_HOSTS = ['*']

SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Vienna'

USE_THOUSAND_SEPARATOR = True

# Application definition

# replace django.contrib.auth.models.User by implementation
# allowing to login via email address
AUTH_USER_MODEL = 'email_auth.User'

AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {
        'min_length': 6,
    }
}]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'email_auth',
    'polymorphic',
    # deprecated: 'djangocms_admin_style',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'djangocms_text_ckeditor',
    'django_select2',
    'cmsplugin_cascade',
    'cmsplugin_cascade.clipboard',
    'cmsplugin_cascade.sharable',
    'cmsplugin_cascade.extra_fields',
    'cmsplugin_cascade.icon',
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
    'post_office',
    'haystack',
    'shop',
    'shop_stripe',
    'myshop',
]
if SHOP_TUTORIAL in ['i18n_commodity', 'i18n_smartcard', 'i18n_polymorphic']:
    INSTALLED_APPS.append('parler')

MIDDLEWARE_CLASSES = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
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
    'cms.middleware.utils.ApphookReloadMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

MIGRATION_MODULES = {
    'myshop': 'myshop.migrations.{}'.format(SHOP_TUTORIAL)
}

ROOT_URLCONF = 'myshop.urls'

WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(WORK_DIR, SHOP_TUTORIAL, 'db.sqlite3'),
    }
}

if os.getenv('POSTGRES_DB') and os.getenv('POSTGRES_USER'):
    # override database with
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
    }

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'en'

if SHOP_TUTORIAL in ['i18n_smartcard', 'i18n_commodity', 'i18n_polymorphic']:
    USE_I18N = True

    LANGUAGES = (
        ('en', "English"),
        ('de', "Deutsch"),
    )

    PARLER_DEFAULT_LANGUAGE = 'en'

    PARLER_LANGUAGES = {
        1: (
            {'code': 'de'},
            {'code': 'en'},
        ),
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
        1: ({
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
        },)
    }
else:
    USE_I18N = False

USE_L10N = True

USE_TZ = True

USE_X_FORWARDED_HOST = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(WORK_DIR, SHOP_TUTORIAL, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', os.path.join(WORK_DIR, 'static'))

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

STATICFILES_FINDERS = [
    'myshop.finders.FileSystemFinder',  # or 'django.contrib.staticfiles.finders.FileSystemFinder',
    'myshop.finders.AppDirectoriesFinder',  # or 'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
    'compressor.finders.CompressorFinder',
]

STATICFILES_DIRS = [
    ('node_modules', os.path.join(PROJECT_ROOT, 'node_modules')),
]


TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'DIRS': [],
    'OPTIONS': {
        'context_processors': (
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.template.context_processors.csrf',
            'django.template.context_processors.request',
            'django.contrib.messages.context_processors.messages',
            'sekizai.context_processors.sekizai',
            'cms.context_processors.cms_settings',
            'shop.context_processors.customer',
            'shop.context_processors.ng_model_options',
            'shop_stripe.context_processors.public_keys',
        )
    }
}]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REDIS_HOST = os.getenv('REDIS_HOST')

if REDIS_HOST:
    SESSION_ENGINE = 'redis_sessions.session'
    SESSION_SAVE_EVERY_REQUEST = True

    SESSION_REDIS = {
        'host': REDIS_HOST,
        'port': 6379,
        'db': 0,
        'prefix': 'session-{}'.format(SHOP_TUTORIAL),
        'socket_timeout': 1
    }
    if six.PY3:
        # Use the latest protocol version (default)                                                                                                                                                           
        PICKLE_V=-1
    else:
        #py2 compatibility                                                                                                                                                                                    
        PICKLE_V=2

    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': 'redis://{}:6379/1'.format(REDIS_HOST),
             "OPTIONS": {
                 "PICKLE_VERSION": PICKLE_V,                                                                                                
	         }
        },
        'compressor': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': 'redis://{}:6379/2'.format(REDIS_HOST),
        },
        'select2': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }

    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 3600

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
    'formatters': {
        'simple': {
            'format': '[%(asctime)s %(module)s] %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'post_office': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

SILENCED_SYSTEM_CHECKS = ['auth.W004']

FIXTURE_DIRS = [os.path.join(WORK_DIR, SHOP_TUTORIAL, 'fixtures')]

############################################
# settings for sending mail

EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', 'localhost')
EMAIL_PORT = os.getenv('DJANGO_EMAIL_PORT', 25)
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_USER', 'no-reply@localhost')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_PASSWORD', 'smtp-secret')
EMAIL_USE_TLS = bool(os.getenv('DJANGO_EMAIL_USE_TLS', '1'))
DEFAULT_FROM_EMAIL = os.getenv('DJANGO_EMAIL_FROM', 'no-reply@localhost')
EMAIL_REPLY_TO = os.getenv('DJANGO_EMAIL_REPLY_TO', 'info@localhost')
EMAIL_BACKEND = 'post_office.EmailBackend'


############################################
# settings for third party Django apps

NODE_MODULES_URL = STATIC_URL + 'node_modules/'

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(PROJECT_ROOT, 'node_modules'),
]

COERCE_DECIMAL_TO_STRING = True

FSM_ADMIN_FORCE_PERMIT = True

ROBOTS_META_TAGS = ('noindex', 'nofollow')

SERIALIZATION_MODULES = {'json': str('shop.money.serializers')}

############################################
# settings for django-restframework and plugins

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'shop.rest.money.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # can be disabled for production environments
    ),
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #   'rest_framework.authentication.TokenAuthentication',
    # ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 12,
}

############################################
# settings for storing session data

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_SAVE_EVERY_REQUEST = True


############################################
# settings for storing files and images

FILER_ADMIN_ICON_SIZES = ('16', '32', '48', '80', '128')

FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True

FILER_DUMP_PAYLOAD = False

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

THUMBNAIL_HIGH_RESOLUTION = False

THUMBNAIL_OPTIMIZE_COMMAND = {
    'gif': '/usr/bin/optipng {filename}',
    'jpeg': '/usr/bin/jpegoptim {filename}',
    'png': '/usr/bin/optipng {filename}'
}

THUMBNAIL_PRESERVE_EXTENSIONS = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)


############################################
# settings for django-cms and its plugins

CMS_TEMPLATES = [
    ('myshop/pages/default.html', _("Default Page")),
    ('myshop/pages/test.html', _("Test Page")),  # to show strides rendering via {% render_cascade ... %}
]

CMS_CACHE_DURATIONS = {
    'content': 600,
    'menus': 3600,
    'permissions': 86400,
}

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

CMSPLUGIN_CASCADE_PLUGINS = [
    'cmsplugin_cascade.segmentation',
    'cmsplugin_cascade.generic',
    'cmsplugin_cascade.icon',
    'cmsplugin_cascade.leaflet',
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
    'plugins_with_extra_render_templates': {
        'CustomSnippetPlugin': [
            ('shop/catalog/product-heading.html', _("Product Heading")),
            ('myshop/catalog/manufacturer-filter.html', _("Manufacturer Filter")),
        ],
        'ShopAddToCartPlugin': [
            (None, _("Default")),
            ('myshop/catalog/commodity-add2cart.html', _("Add Commodity to Cart")),
        ],
    },
    'plugins_with_sharables': {
        'BootstrapImagePlugin': ['image_shapes', 'image_width_responsive', 'image_width_fixed',
                                 'image_height', 'resize_options'],
        'BootstrapPicturePlugin': ['image_shapes', 'responsive_heights', 'image_size', 'resize_options'],
    },
    'leaflet': {
        'tilesURL': 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}',
        'accessToken': 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
        'apiKey': 'AIzaSyD71sHrtkZMnLqTbgRmY_NsO0A9l9BQmv4',
    },
    'bookmark_prefix': '/',
    'segmentation_mixins': [
        ('shop.cascade.segmentation.EmulateCustomerModelMixin', 'shop.cascade.segmentation.EmulateCustomerAdminMixin'),
    ],
    'allow_plugin_hiding': True,
}

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'skin': 'moono',
    'toolbar': 'CMS',
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
    'stylesSet': format_lazy('default:{}', reverse_lazy('admin:cascade_texticon_wysiwig_config')),
}

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

SELECT2_CSS = 'node_modules/select2/dist/css/select2.min.css'
SELECT2_JS = 'node_modules/select2/dist/js/select2.min.js'


COMPRESS_CACHE_BACKEND = 'compressor'

#############################################
# settings for full index text search (Haystack)

ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://{}:9200/'.format(ELASTICSEARCH_HOST),
        'INDEX_NAME': 'myshop-{}-en'.format(SHOP_TUTORIAL),
    },
}
if USE_I18N:
    HAYSTACK_CONNECTIONS['de'] = {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://{}:9200/'.format(ELASTICSEARCH_HOST),
        'INDEX_NAME': 'myshop-{}-de'.format(SHOP_TUTORIAL),
    }

HAYSTACK_ROUTERS = [
    'shop.search.routers.LanguageRouter',
]

############################################
# settings for django-shop and its plugins

SHOP_VALUE_ADDED_TAX = Decimal(19)
SHOP_DEFAULT_CURRENCY = 'EUR'
SHOP_PRODUCT_SUMMARY_SERIALIZER = 'myshop.serializers.ProductSummarySerializer'
if SHOP_TUTORIAL in ['i18n_polymorphic', 'polymorphic']:
    SHOP_CART_MODIFIERS = ['myshop.polymorphic_modifiers.MyShopCartModifier']
else:
    SHOP_CART_MODIFIERS = ['shop.modifiers.defaults.DefaultCartModifier']
SHOP_CART_MODIFIERS.extend([
    'shop.modifiers.taxes.CartExcludedTaxModifier',
    'myshop.modifiers.PostalShippingModifier',
    'myshop.modifiers.CustomerPickupModifier',
    'shop.modifiers.defaults.PayInAdvanceModifier',
])

SHOP_EDITCART_NG_MODEL_OPTIONS = "{updateOn: 'default blur', debounce: {'default': 2500, 'blur': 0}}"

SHOP_ORDER_WORKFLOWS = [
    'shop.payment.defaults.ManualPaymentWorkflowMixin',
    'shop.payment.defaults.CancelOrderWorkflowMixin',
]

if 'shop_stripe' in INSTALLED_APPS:
    SHOP_CART_MODIFIERS.append('myshop.modifiers.StripePaymentModifier')
    SHOP_ORDER_WORKFLOWS.append('shop_stripe.payment.OrderWorkflowMixin')

if 'shop_sendcloud' in INSTALLED_APPS:
    SHOP_CART_MODIFIERS.append('shop_sendcloud.modifiers.SendcloudShippingModifier')
    SHOP_ORDER_WORKFLOWS.append('shop_sendcloud.shipping.OrderWorkflowMixin')

if SHOP_TUTORIAL in ['i18n_polymorphic', 'polymorphic']:
    SHOP_ORDER_WORKFLOWS.append('shop.shipping.delivery.PartialDeliveryWorkflowMixin')
else:
    SHOP_ORDER_WORKFLOWS.append('shop.shipping.defaults.CommissionGoodsWorkflowMixin')

SHOP_STRIPE = {
    'PUBKEY': 'pk_test_HlEp5oZyPonE21svenqowhXp',
    'APIKEY': 'sk_test_xUdHLeFasmOUDvmke4DHGRDP',
    'PURCHASE_DESCRIPTION': _("Thanks for purchasing at MyShop"),
}

try:
    from .private_settings import *  # NOQA
except ImportError:
    pass
