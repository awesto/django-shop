# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

from shop.admin.defaults import customer
from shop.models.order import OrderModel

# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL in ('commodity', 'i18n_commodity'):
    from shop.admin.defaults import commodity
    from . import order
elif settings.SHOP_TUTORIAL == 'smartcard':
    from . import manufacturer
    from . import smartcard
    from . import order
elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from . import manufacturer
    from . import i18n_smartcard
    from . import order
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from . import manufacturer
    from .polymorphic import product, order

__all__ = ['OrderModel', 'commodity', 'customer']

admin.site.site_header = "Django-SHOP administration"
