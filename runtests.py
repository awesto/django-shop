#!/usr/bin/env python
import os
import sys
import optparse
import django

from django.conf import settings
from django import VERSION as DJANGO_VERSION


parser = optparse.OptionParser()
opts, args = parser.parse_args()

if not settings.configured:
    directory = os.path.abspath('%s' % os.path.dirname(__file__))
    db_name = 'test_django_shop'

    settings.configure(

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test.sqlite',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
            },
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            # Uncomment the next line to enable the admin:
            'django.contrib.admin',
            # Uncomment the next line to enable admin documentation:
            'django.contrib.admindocs',
            'polymorphic', # We need polymorphic installed for the shop
            'shop', # The django SHOP application
            'shop.addressmodel',
            'project', # the test project application
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        ROOT_URLCONF='testapp.urls',
        SITE_ID=1,
        STATIC_URL='%s/testapp/static/' % directory,
        TEMPLATE_CONTEXT_PROCESSORS=(
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.debug',
            'django.core.context_processors.i18n',
            'django.core.context_processors.media',
            'django.core.context_processors.static',
            'django.contrib.messages.context_processors.messages',
            'django.core.context_processors.request',
        ),
        TEMPLATE_DIRS=(
        ),

        # In tests, compressor has a habit of choking on failing tests & masking the real error.
        STATIC_ROOT='static/',

        # Increase speed in 1.4.
        PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',),
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner',

        # The shop settings:
        SHOP_CART_MODIFIERS= ['shop.cart.modifiers.rebate_modifiers.BulkRebateModifier'],
        SHOP_SHIPPING_BACKENDS=['shop.shipping.backends.flat_rate.FlatRateShipping'],
        SHOP_PAYMENT_BACKENDS=[
            'shop.payment.backends.pay_on_delivery.PayOnDeliveryBackend'
        ],

        # Shop module settings
        SHOP_SHIPPING_FLAT_RATE = '10' # That's just for the flat rate shipping backend
    )


def run_django_tests():
    apps = ['shop', 'addressmodel', ]
    if DJANGO_VERSION >= (1, 6):
        apps = ['shop', 'shop.addressmodel', ]
        settings.TEST_RUNNER = 'django.test.runner.DiscoverRunner'
    if DJANGO_VERSION >= (1, 7):
        django.setup()
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(args or apps)
    sys.exit(failures)


if __name__ == '__main__':
    run_django_tests()
