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
if settings.SHOP_TUTORIAL in ('commodity', 'i18n_commodity'):
    from shop.admin.defaults import commodity

    @admin.register(Order)
    class OrderAdmin(OrderAdmin):
        pass

elif settings.SHOP_TUTORIAL in ('smartcard', 'i18n_smartcard'):
    from . import manufacturer
    if settings.SHOP_TUTORIAL == 'smartcard':
        from . import smartcard
    else:
        from . import i18n_smartcard

    @admin.register(Order)
    class OrderAdmin(PrintOrderAdminMixin, OrderAdmin):
        pass

elif settings.SHOP_TUTORIAL == 'polymorphic':
    from . import manufacturer
    from . import i18n_polymorphic

    @admin.register(Order)
    class OrderAdmin(PrintOrderAdminMixin, DeliveryOrderAdminMixin, OrderAdmin):
        pass


__all__ = ['commodity', 'customer']

admin.site.site_header = "Django-SHOP administration"
