# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.admin.order import BaseOrderAdmin, OrderPaymentInline


class OrderAdmin(BaseOrderAdmin):
    """
    Admin class to be used for Order model :class:`shop.models.defaults.order`
    """
    def get_fields(self, request, obj=None):
        fields = list(super(OrderAdmin, self).get_fields(request, obj))
        fields.extend(['shipping_address_text', 'billing_address_text'])
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(OrderAdmin, self).get_readonly_fields(request, obj))
        readonly_fields.extend(['shipping_address_text', 'billing_address_text'])
        return readonly_fields

    def get_search_fields(self, request):
        search_fields = list(super(OrderAdmin, self).get_search_fields(request))
        search_fields.extend(['number', 'shipping_address_text', 'billing_address_text'])
        return search_fields

    def get_inline_instances(self, request, obj=None):
        inline_instances = list(super(OrderAdmin, self).get_inline_instances(request, obj))
        inline_instances.append(OrderPaymentInline(self.model, self.admin_site))
        return inline_instances
