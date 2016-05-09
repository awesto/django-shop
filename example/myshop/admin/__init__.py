# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from shop.admin.customer import CustomerProxy, CustomerAdmin
from shop.models.order import OrderModel

__all__ = ['OrderModel', 'commodity']

# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL == 'commodity' or settings.SHOP_TUTORIAL == 'i18n_commodity':
    from shop.admin import commodity
elif settings.SHOP_TUTORIAL == 'smartcard':
    from . import manufacturer
    from .smartcard import smartcard, order
elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from . import manufacturer
    from . import i18n_smartcard
    from .smartcard import order
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from . import manufacturer
    from .polymorphic import product, order

admin.site.register(CustomerProxy, CustomerAdmin)
