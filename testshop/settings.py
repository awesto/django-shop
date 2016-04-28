# -*- coding: utf-8 -*-
from __future__ import unicode_literals

SECRET_KEY = 'secret'

INSTALLED_APPS = (
    'django.contrib.auth',
    'email_auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'treebeard',
    'cms',
    'menus',
    'post_office',
    'filer',
    'easy_thumbnails',
    'shop',
    'testshop',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shop.middleware.CustomerMiddleware',
)

STATIC_URL = '/static/'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
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
        )
    }
}]

SILENCED_SYSTEM_CHECKS = ['auth.W004']

SHOP_APP_LABEL = 'testshop'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SERIALIZATION_MODULES = {'shop': 'shop.money.serializers'}

AUTH_USER_MODEL = 'email_auth.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
