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

if settings.SHOP_TUTORIAL in ('commodity', 'i18n_commodity'):
    Product = import_string('shop.models.defaults.commodity.Commodity')
elif settings.SHOP_TUTORIAL == 'smartcard':
    Product = import_string('myshop.models.smartcard.SmartCard')
elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    Product = import_string('myshop.models.i18n_smartcard.SmartCard')
elif settings.SHOP_TUTORIAL == 'polymorphic':
    Product = import_string('myshop.models.polymorphic.product.Product')
else:
    raise NotImplementedError("Unknown settings for SHOP_TUTORIAL: {}".format(settings.SHOP_TUTORIAL))


class ProductSummarySerializer(ProductSummarySerializerBase):
    media = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_url', 'product_model', 'price',
            'media', 'caption')

    def get_media(self, product):
        return self.render_html(product, 'media')


class ProductDetailSerializer(ProductDetailSerializerBase):
    class Meta:
        model = Product
        exclude = ('active', 'polymorphic_ctype',)


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
            variant = product.get_product_variant(extra.get('product_code'))
        except product.DoesNotExist:
            variant = product.smartphone_set.first()
        instance = {
            'product': product.id,
            'unit_price': variant.unit_price,
            'extra': {'product_code': variant.product_code, 'storage': variant.storage}
        }
        return instance


class ProductSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to search over all products in this shop
    """
    media = serializers.SerializerMethodField()

    class Meta(ProductSearchSerializerBase.Meta):
        fields = ProductSearchSerializerBase.Meta.fields + ('media', 'caption')
        index_classes = myshop_search_index_classes

    def get_media(self, search_result):
        return search_result.search_media


class CatalogSearchSerializer(ProductSearchSerializer):
    """
    Serializer to restrict products in the catalog
    """
    def get_media(self, search_result):
        return search_result.catalog_media
