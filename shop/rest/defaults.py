# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .bases import (BaseCustomerSerializer, BaseOrderItemSerializer,
                    get_product_summary_serializer_class)


class CustomerSerializer(BaseCustomerSerializer):
    """
    This CustomerSerializer shall be used as a default, if used in combination with
    :class:`shop.models.defaults.customer.CustomerSerializer`.
    Replace it by another serializer, for alternative Customer Models.
    """
    salutation = serializers.CharField(source='get_salutation_display', read_only=True)

    class Meta(BaseCustomerSerializer.Meta):
        fields = BaseCustomerSerializer.Meta.fields + ('salutation',)


class OrderItemSerializer(BaseOrderItemSerializer):
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")

    class Meta(BaseOrderItemSerializer.Meta):
        fields = ('line_total', 'unit_price', 'quantity', 'summary', 'extra')

    def get_summary(self, order_item):
        label = self.context.get('render_label', 'order')
        serializer_class = get_product_summary_serializer_class()
        serializer = serializer_class(order_item.product, context=self.context,
                                      read_only=True, label=label)
        return serializer.data
