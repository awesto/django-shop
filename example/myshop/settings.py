# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from decimal import Decimal

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

##########################
# Django specific settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
    }
}

SITE_ID = 1


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

INSTALLED_APPS = (
    'django.contrib.auth',
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
    'cmsplugin_cascade.sharable',
    'cmsplugin_cascade.extra_fields',
    'cms_bootstrap3',
    'adminsortable',
    'rest_framework',
    'djangular',
    'cms',
    'menus',
    'mptt',
    'nodebow',
    'south',
    'compressor',
    'sekizai',
    'sass_processor',
    'filer',
    'easy_thumbnails',
    'easy_thumbnails.optimize',
    'parler',
    'shop',
    'myshop',
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-de'

LANGUAGES = (
    ('en', 'English'),
    ('de', 'Deutsch'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.environ.get('DJANGO_UPLOAD_DIR'), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.environ.get('STATIC_ROOT', '/var/tmp/static_root/'))

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# A list of locations of additional static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
    #'compressor.finders.CompressorFinder',
    'nodebow.finders.BowerComponentsFinder',
)

# Override this, make this unique, and don't share it with anybody.
SECRET_KEY = 'secret'

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_DEBUG = DEBUG

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'cms.context_processors.media',
    'stofferia.context_processors.global_context',
    'sekizai.context_processors.sekizai',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SOUTH_MIGRATION_MODULES = {
    'example': 'example.south_migrations',
}

# Monkey patches:
# Backport numberformat from Django-1.8
from django.utils import numberformat
from shop.patches import numberformat as patched_numberformat
numberformat.format = patched_numberformat.format


###############################################
# django-cms, and CMS plugins specific settings

CMS_TEMPLATES = (
    ('stofferia/default-page.html', 'Default Page Template'),
    ('stofferia/home-page.html', 'Home Page Template'),
    ('stofferia/textile-list.html', 'Textile Template'),
)

CMS_SEO_FIELDS = True

CMS_LANGUAGES = {
    'default': {
        'fallbacks': ['de', 'en'],
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    },
    1: ({
        'public': True,
        'code': 'de',
        'hide_untranslated': False,
        'name': 'Deutsch',
        'redirect_on_fallback': True,
    }, {
        'public': True,
        'code': 'en',
        'hide_untranslated': False,
        'name': 'English',
        'redirect_on_fallback': True,
    },)
}

CMS_PERMISSION = False

COLUMN_GLOSSARY = {
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
    'Hero Container': {
        'plugins': ['BootstrapRowPlugin'],
        'parent_classes': {'BootstrapRowPlugin': []},
        'require_parent': False,
        'glossary': COLUMN_GLOSSARY,
    },
    'Main Content Container': {
        'plugins': ['BootstrapRowPlugin', 'ShopCartPlugin'],
        'parent_classes': {'BootstrapRowPlugin': []},
        'require_parent': False,
        'glossary': COLUMN_GLOSSARY,
    },
    'Products List': {
        'plugins': ['BootstrapRowPlugin', 'TextPlugin'],
        'parent_classes': {'BootstrapRowPlugin': []},
        'require_parent': False,
        'glossary': COLUMN_GLOSSARY,
    },
    'Commodity Detail': {
        'plugins': ['BootstrapRowPlugin', 'TextPlugin'],
        'parent_classes': {'BootstrapRowPlugin': []},
        'require_parent': False,
        'glossary': COLUMN_GLOSSARY,  # TODO: adopt 'container_max_widths' to real column widths
    },
}

CMSPLUGIN_CASCADE_PLUGINS = ('shop.cascade', 'cmsplugin_cascade.bootstrap3',)
#CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.link', 'cmsplugin_cascade.bootstrap3',)

#CMS_CASCADE_LEAF_PLUGINS = ('TextLinkPlugin',)

CMSPLUGIN_CASCADE_DEPENDENCIES = {
#    'stofferia/js/admin/linkplugin.js': 'cascade/js/ring.js',
}

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'skin': 'moono',
    'toolbar': 'CMS',
}


###############################
# django-shop specific settings

SHOP_CART_MODIFIERS = (
    'stofferia.modifiers.StofferiaCartModifier',
    'shop.modifiers.taxes.CartExcludedTaxModifier',
    'shop.modifiers.defaults.SelfCollectionModifier',
    'stofferia.modifiers.PostalShippingModifier',
    'shop.modifiers.defaults.PayInAdvanceModifier',
    'stofferia.stripe_payment.StripePaymentModifier',
)

SHOP_APP_LABEL = 'myshop'
SHOP_VALUE_ADDED_TAX = Decimal(19)
SHOP_DEFAULT_CURRENCY = 'EUR'

###################
# other Django apps

COMPRESS_ENABLED = False

SASS_PROCESSOR_INCLUDE_DIRS = (
    os.path.abspath(os.path.join(PROJECT_DIR, os.pardir, 'node_modules')),
)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'shop.money.rest.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

PARLER_DEFAULT_LANGUAGE = 'de'

PARLER_LANGUAGES = {
    1: (
        {'code': 'de'},
        {'code': 'en'},
    ),
    'default': {
        'fallback': 'de',
    },
}

FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True

FILER_DUMP_PAYLOAD = False

FILER_ADMIN_ICON_SIZES = ('16', '32', '48', '80', '128',)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_HIGH_RESOLUTION = False

THUMBNAIL_PRESERVE_EXTENSIONS = True

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/opt/local/bin/optipng {filename}',
    'gif': '/opt/local/bin/optipng {filename}',
    'jpeg': '/opt/local/bin/jpegoptim {filename}',
}


##############################
# Override with local settings
try:
    from ._local_settings import *
except ImportError:
    pass
