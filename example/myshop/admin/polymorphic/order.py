# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from shop.admin.order import PrintOrderAdminMixin, BaseOrderAdmin
from shop.models.defaults.order import Order
from shop.admin.delivery import DeliveryOrderAdminMixin


@admin.register(Order)
class OrderAdmin(PrintOrderAdminMixin, DeliveryOrderAdminMixin, BaseOrderAdmin):
    search_fields = BaseOrderAdmin.search_fields + ('shipping_address_text',
        'billing_address_text', 'number',)
    fields = BaseOrderAdmin.fields + (('shipping_address_text', 'billing_address_text',),)
