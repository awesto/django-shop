# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.serializers.bases import ProductSerializer


class ProductSummarySerializer(ProductSerializer):
    """
    Default serializer to create a summary from our Product model.
    In case the Product model is polymorphic, this shall serialize the smallest common denominator
    of all product information.
    """
    caption = serializers.SerializerMethodField(help_text="Returns the content from caption field if available")

    class Meta(ProductSerializer.Meta):
        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media', 'caption']

    def get_caption(self, product):
        return getattr(product, 'caption', None)
