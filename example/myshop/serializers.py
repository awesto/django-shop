# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template import RequestContext
from django.template.base import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe, SafeText
from rest_framework import serializers
from shop.rest.serializers import ProductSummarySerializerBase, ProductDetailSerializerBase
from shop.search.serializers import ProductSearchSerializer as ProductSearchSerializerBase
from .models.product import Product
from .search_indexes import CommodityIndex


class ProductSummarySerializer(ProductSummarySerializerBase):
    media = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_url', 'product_type', 'product_model', 'price',
                  'media',)

    def get_media(self, product):
        return self.render_html(product, 'media')


class ProductDetailSerializer(ProductDetailSerializerBase):
    class Meta:
        model = Product
        exclude = ('active',)


class ProductSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to search over all products in this shop
    """
    app_label = settings.SHOP_APP_LABEL.lower()

    class Meta(ProductSearchSerializerBase.Meta):
        index_classes = (CommodityIndex,)
        fields = ProductSearchSerializerBase.Meta.fields + ('description', 'media', 'overlay')
        field_aliases = {'q': 'text'}


class CommoditySearchSerializer(ProductSearchSerializer):
    class Meta(ProductSearchSerializer.Meta):
        index_classes = (CommodityIndex,)
        field_aliases = {'q': 'autocomplete'}
