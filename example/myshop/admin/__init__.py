# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from shop.admin.customer import CustomerProxy, CustomerAdmin
from shop.models.order import OrderModel


# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL == 'commodity' or settings.SHOP_TUTORIAL == 'i18n_commodity':
    from shop.admin import commodity
elif settings.SHOP_TUTORIAL == 'simple':
    from . import manufacturer
    from .simple import smartcard, order
elif settings.SHOP_TUTORIAL == 'i18n':
    from . import manufacturer
    from .i18n import smartcard
    from .simple import order
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from . import manufacturer
    from .polymorphic import product, order

admin.site.register(CustomerProxy, CustomerAdmin)
