from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.utils.text import format_lazy

DEBUG = True

ROOT_URLCONF = 'testshop.urls'

SECRET_KEY = 'test'

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'DIRS': [],
    'OPTIONS': {
        'context_processors': [
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
        ]
    }
}, {
    'BACKEND': 'post_office.template.backends.post_office.PostOfficeTemplates',
    'APP_DIRS': True,
    'DIRS': [],
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.template.context_processors.request',
        ]
    }
}]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shop.middleware.CustomerMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'email_auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'jsonfield',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'django_fsm',
    'fsm_admin',
    'filer',
    'easy_thumbnails',
    'treebeard',
    'menus',
    'sekizai',
    'cms',
    'adminsortable2',
    'djangocms_text_ckeditor',
    'cmsplugin_cascade',
    'cmsplugin_cascade.clipboard',
    'cmsplugin_cascade.extra_fields',
    'cmsplugin_cascade.icon',
    'cmsplugin_cascade.sharable',
    'cmsplugin_cascade.segmentation',
    'post_office',
    'shop',
    'testshop',
]

USE_I18N = False

USE_L10N = True

USE_TZ = True

TIME_ZONE = 'UTC'

LANGUAGES = [
    ('en', 'English'),
]

LANGUAGE_CODE = 'en'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CMS_TEMPLATES = [
    ('page.html', "Default Page"),
]

CMS_PLACEHOLDER_CONF = {
    'Main Content': {
        'plugins': ['BootstrapContainerPlugin'],
    },
}

CMSPLUGIN_CASCADE_PLUGINS = [
    'cmsplugin_cascade.bootstrap4',
    'cmsplugin_cascade.segmentation',
    'cmsplugin_cascade.generic',
    'cmsplugin_cascade.icon',
    'cmsplugin_cascade.leaflet',
    'cmsplugin_cascade.link',
    'shop.cascade',
]

CMSPLUGIN_CASCADE = {
    'link_plugin_classes': [
        'shop.cascade.plugin_base.CatalogLinkPluginBase',
        'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
        'shop.cascade.plugin_base.CatalogLinkForm',
    ],
    'alien_plugins': ['TextPlugin', 'TextLinkPlugin', 'AcceptConditionPlugin'],
    'bootstrap4': {
        'template_basedir': 'angular-ui',
    },
    'segmentation_mixins': [
        ('shop.cascade.segmentation.EmulateCustomerModelMixin', 'shop.cascade.segmentation.EmulateCustomerAdminMixin'),
    ],
}

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_PRESERVE_EXTENSIONS = True,

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
    'stylesSet': format_lazy('default:{}', reverse_lazy('admin:cascade_texteditor_config')),
}

SILENCED_SYSTEM_CHECKS = ['auth.W004']

SHOP_APP_LABEL = 'testshop'

SHOP_CART_MODIFIERS = [
    'shop.modifiers.defaults.DefaultCartModifier',
    'shop.modifiers.taxes.CartIncludeTaxModifier',
    'shop.payment.modifiers.PayInAdvanceModifier',
    'shop.shipping.modifiers.SelfCollectionModifier',
]

SHOP_ORDER_WORKFLOWS = [
    'shop.payment.workflows.ManualPaymentWorkflowMixin',
    'shop.payment.workflows.CancelOrderWorkflowMixin',
    'shop.shipping.workflows.PartialDeliveryWorkflowMixin',
]

AUTH_USER_MODEL = 'email_auth.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'shop.serializers.auth.LoginSerializer',
}

POST_OFFICE = {
    'TEMPLATE_ENGINE': 'post_office',
}
