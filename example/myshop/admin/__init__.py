# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib import admin
from shop.admin.customer import CustomerProxy, CustomerAdmin
from shop.admin.order import (PrintOrderAdminMixin, BaseOrderAdmin, OrderPaymentInline, OrderItemInline)
from shop.models.order import OrderModel
#from . import product
from . import properties

if settings.MYSHOP_TUTORIAL == '02':
    from .simple import smartcard
else:
    from .i18n import smartcard

admin.site.register(CustomerProxy, CustomerAdmin)


@admin.register(OrderModel)
class OrderAdmin(PrintOrderAdminMixin, BaseOrderAdmin):
    search_fields = BaseOrderAdmin.search_fields + ('shipping_address_text',
        'billing_address_text', 'number',)
    fields = BaseOrderAdmin.fields + (('shipping_address_text', 'billing_address_text',),)
    inlines = (OrderItemInline, OrderPaymentInline,)
