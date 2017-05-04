# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.safestring import mark_safe

from rest_framework import serializers

from shop.serializers.bases import ProductSerializer
from shop.search.serializers import ProductSearchSerializer as BaseProductSearchSerializer

from myshop.search_indexes import myshop_search_index_classes

__all__ = ['ProductSummarySerializer', 'ProductSearchSerializer', 'CatalogSearchSerializer']


class ProductSummarySerializer(ProductSerializer):
    media = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media', 'caption']

    def get_media(self, product):
        return self.render_html(product, 'media')

if settings.SHOP_TUTORIAL in ['commodity', 'i18n_commodity']:

    class ProductDetailSerializer(ProductSerializer):
        class Meta(ProductSerializer.Meta):
            fields = ['product_name', 'slug', 'unit_price', 'product_code']

    __all__.append('ProductDetailSerializer')

elif settings.SHOP_TUTORIAL in ['smartcard', 'i18n_smartcard']:

    class ProductDetailSerializer(ProductSerializer):
        class Meta(ProductSerializer.Meta):
            fields = ['product_name', 'slug', 'unit_price', 'manufacturer', 'card_type', 'speed',
                      'product_code', 'storage']

    __all__.append('ProductDetailSerializer')

elif settings.SHOP_TUTORIAL in ['i18n_polymorphic', 'polymorphic']:

    from .polymorphic import (SmartCardSerializer, SmartPhoneSerializer, AddSmartPhoneToCartSerializer)

    __all__.extend(['SmartCardSerializer', 'SmartPhoneSerializer', 'AddSmartPhoneToCartSerializer'])


class ProductSearchSerializer(BaseProductSearchSerializer):
    """
    Serializer to search over all products in this shop
    """
    media = serializers.SerializerMethodField()

    class Meta(BaseProductSearchSerializer.Meta):
        fields = BaseProductSearchSerializer.Meta.fields + ['media', 'caption']
        field_aliases = {'q': 'text'}
        search_fields = ['text']
        index_classes = myshop_search_index_classes

    def get_media(self, search_result):
        return mark_safe(search_result.search_media)


class CatalogSearchSerializer(BaseProductSearchSerializer):
    """
    Serializer to restrict products in the catalog
    """
    media = serializers.SerializerMethodField()

    class Meta(BaseProductSearchSerializer.Meta):
        fields = BaseProductSearchSerializer.Meta.fields + ['media', 'caption']
        field_aliases = {'q': 'autocomplete'}
        search_fields = ['autocomplete']
        index_classes = myshop_search_index_classes

    def get_media(self, search_result):
        return mark_safe(search_result.catalog_media)
