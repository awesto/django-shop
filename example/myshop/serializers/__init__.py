# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe

from rest_framework import serializers

from shop.serializers.bases import ProductSerializer
from shop.search.serializers import ProductSearchSerializer as ProductSearchSerializerBase

from myshop.search_indexes import myshop_search_index_classes

__all__ = ['ProductSummarySerializer', 'ProductSearchSerializer', 'CatalogSearchSerializer']

# if settings.SHOP_TUTORIAL in ['commodity', 'i18n_commodity']:
#     Product = import_string('shop.models.defaults.commodity.Commodity')
# elif settings.SHOP_TUTORIAL == 'smartcard':
#     Product = import_string('myshop.models.smartcard.SmartCard')
# elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
#     Product = import_string('myshop.models.i18n_smartcard.SmartCard')
# elif settings.SHOP_TUTORIAL == 'polymorphic':
#     Product = import_string('myshop.models.polymorphic.product.Product')
#     from .polymorphic import (SmartCardSerializer, AddSmartCardToCartSerializer,
#                               SmartPhoneSerializer, AddSmartPhoneToCartSerializer)
#
#     __all__.extend(['SmartCardSerializer', 'AddSmartCardToCartSerializer',
#                     'SmartPhoneSerializer', 'AddSmartPhoneToCartSerializer'])
# else:
#     raise NotImplementedError("Unknown settings for SHOP_TUTORIAL: {}".format(settings.SHOP_TUTORIAL))

if settings.SHOP_TUTORIAL == 'polymorphic':
    from .polymorphic import (SmartCardSerializer, AddSmartCardToCartSerializer,
                              SmartPhoneSerializer, AddSmartPhoneToCartSerializer)
    __all__.extend(['SmartCardSerializer', 'AddSmartCardToCartSerializer',
                    'SmartPhoneSerializer', 'AddSmartPhoneToCartSerializer'])


class ProductSummarySerializer(ProductSerializer):
    media = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        #model = Product
        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media', 'caption']

    def get_media(self, product):
        return self.render_html(product, 'media')


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        #model = Product
        exclude = ['active', 'polymorphic_ctype']


class ProductSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to search over all products in this shop
    """
    media = serializers.SerializerMethodField()

    class Meta(ProductSearchSerializerBase.Meta):
        fields = ProductSearchSerializerBase.Meta.fields + ('media', 'caption')
        field_aliases = {'q': 'text'}
        search_fields = ['text']
        index_classes = myshop_search_index_classes

    def get_media(self, search_result):
        return mark_safe(search_result.search_media)


class CatalogSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to restrict products in the catalog
    """
    media = serializers.SerializerMethodField()

    class Meta(ProductSearchSerializerBase.Meta):
        fields = ProductSearchSerializerBase.Meta.fields + ('media', 'caption')
        field_aliases = {'q': 'autocomplete'}
        search_fields = ['autocomplete']
        index_classes = myshop_search_index_classes

    def get_media(self, search_result):
        return mark_safe(search_result.catalog_media)
