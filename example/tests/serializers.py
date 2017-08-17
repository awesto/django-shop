# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from shop.serializers.bases import ProductSerializer


class ProductSummarySerializer(ProductSerializer):
    media = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media', 'caption']

    def get_media(self, product):
        return self.render_html(product, 'media')


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ['product_name', 'slug', 'unit_price', 'product_code']
