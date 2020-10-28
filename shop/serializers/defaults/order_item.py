from rest_framework import serializers
from shop.conf import app_settings
from shop.serializers.bases import BaseOrderItemSerializer


class OrderItemSerializer(BaseOrderItemSerializer):
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")

    class Meta(BaseOrderItemSerializer.Meta):
        fields = ['line_total', 'unit_price', 'product_code', 'quantity', 'summary', 'extra']

    def get_summary(self, order_item):
        label = self.context.get('render_label', 'order')
        serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
        serializer = serializer_class(order_item.product, context=self.context,
                                      read_only=True, label=label)
        return serializer.data
