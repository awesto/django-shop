# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from shop.admin.order import PrintOrderAdminMixin, BaseOrderAdmin
from shop.models.defaults.order import Order
from shop.admin.delivery import DeliveryOrderAdminMixin


@admin.register(Order)
class OrderAdmin(PrintOrderAdminMixin, DeliveryOrderAdminMixin, BaseOrderAdmin):
    def get_fields(self, request, obj=None):
        fields = list(super(OrderAdmin, self).get_fields(request, obj))
        fields.extend(['shipping_address_text', 'billing_address_text'])
        return fields

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(OrderAdmin, self).get_readonly_fields(request, obj))
        fields.extend(['shipping_address_text', 'billing_address_text'])
        return fields

    def get_search_fields(self, request):
        fields = list(super(OrderAdmin, self).get_search_fields(request))
        fields.extend(['shipping_address_text', 'billing_address_text', 'number'])
        return fields
