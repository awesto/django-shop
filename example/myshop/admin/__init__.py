# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

from shop.admin.defaults import customer
from shop.admin.defaults.order import OrderAdmin
from shop.models.defaults.order import Order
from shop.admin.order import PrintOrderAdminMixin
from shop.admin.delivery import DeliveryOrderAdminMixin


# models defined by the myshop instance itself
if settings.SHOP_TUTORIAL in ['commodity', 'i18n_commodity']:
    from shop.admin.defaults import commodity

    __all__ = ['customer', 'commodity']
else:
    from . import manufacturer

    if settings.SHOP_TUTORIAL in ['i18n_smartcard', 'smartcard']:
        class OrderAdmin(PrintOrderAdminMixin, OrderAdmin):
            pass

    elif settings.SHOP_TUTORIAL in ['i18n_polymorphic', 'polymorphic']:
        class OrderAdmin(PrintOrderAdminMixin, DeliveryOrderAdminMixin, OrderAdmin):
            pass

    __all__ = ['customer']

admin.site.register(Order, OrderAdmin)

if settings.SHOP_TUTORIAL == 'smartcard':
    from . import smartcard

elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from . import i18n_smartcard

elif settings.SHOP_TUTORIAL == 'polymorphic':
    from . import polymorphic_

elif settings.SHOP_TUTORIAL == 'i18n_polymorphic':
    from . import i18n_polymorphic

elif settings.SHOP_TUTORIAL == 'i18n_dashboard':
    from . import i18n_dashboard

admin.site.site_header = "Django-SHOP administration"
