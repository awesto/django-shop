# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.fields import empty
from shop.rest.serializers import (ProductSummarySerializerBase, ProductDetailSerializerBase,
    AddToCartSerializer)
from shop.search.serializers import ProductSearchSerializer as ProductSearchSerializerBase
from .search_indexes import myshop_search_index_classes

if settings.SHOP_TUTORIAL == 'simple':
    Product = import_string('myshop.models.simple.smartcard.SmartCard')
elif settings.SHOP_TUTORIAL == 'i18n':
    Product = import_string('myshop.models.i18n.smartcard.SmartCard')
else:
    Product = import_string('myshop.models.polymorphic.product.Product')


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


class AddSmartCardToCartSerializer(AddToCartSerializer):
    """
    Modified AddToCartSerializer which handles SmartCards
    """
    def get_instance(self, context, data, extra_args):
        product = context['product']
        extra = context['request'].data.get('extra', {})
        extra.setdefault('product_code', product.product_code)
        instance = {
            'product': product.id,
            'unit_price': product.unit_price,
            'extra': extra,
        }
        return instance


class AddSmartPhoneToCartSerializer(AddToCartSerializer):
    """
    Modified AddToCartSerializer which handles SmartPhones
    """
    def get_instance(self, context, data, extra_args):
        product = context['product']
        extra = data['extra'] if data is not empty else {}
        try:
            variation = product.get_product_variation(extra.get('product_code'))
        except product.DoesNotExist:
            variation = product.smartphone_set.first()
        instance = {
            'product': product.id,
            'unit_price': variation.unit_price,
            'extra': {'product_code': variation.product_code}
        }
        return instance


class ProductSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to search over all products in this shop
    """
    media = serializers.SerializerMethodField()

    class Meta(ProductSearchSerializerBase.Meta):
        fields = ProductSearchSerializerBase.Meta.fields + ('media',)
        index_classes = myshop_search_index_classes

    def get_media(self, search_result):
        return search_result.search_media


class CatalogSearchSerializer(ProductSearchSerializer):
    def get_media(self, search_result):
        return search_result.catalog_media
