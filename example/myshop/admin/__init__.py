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
if settings.SHOP_TUTORIAL == 'commodity':
    from shop.admin.defaults import commodity

else:
    from . import manufacturer

    if 'shop.shipping.workflows.PartialDeliveryWorkflowMixin' in settings.SHOP_ORDER_WORKFLOWS:
        class OrderAdmin(PrintOrderAdminMixin, DeliveryOrderAdminMixin, OrderAdmin):
            pass
    else:
        class OrderAdmin(PrintOrderAdminMixin, OrderAdmin):
            pass

if 'shop_sendcloud' in settings.INSTALLED_APPS:
    from shop_sendcloud.admin import SendCloudOrderAdminMixin

    class OrderAdmin(SendCloudOrderAdminMixin, OrderAdmin):
        pass

admin.site.register(Order, OrderAdmin)

if settings.SHOP_TUTORIAL == 'smartcard':
    if settings.USE_I18N:
        from . import i18n_smartcard
    else:
        from . import smartcard

elif settings.SHOP_TUTORIAL == 'polymorphic':
    if settings.USE_I18N:
        from . import i18n_polymorphic
    else:
        from . import polymorphic_

__all__ = ['commodity', 'customer']

admin.site.site_header = "Django-SHOP administration"
