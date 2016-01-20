# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.fields import empty
from shop.rest.serializers import (ProductSummarySerializerBase, ProductDetailSerializerBase,
    AddToCartSerializer)
from shop.search.serializers import ProductSearchSerializer as ProductSearchSerializerBase
if settings.SHOP_TUTORIAL in ('simple', 'i18n'):
    Product = import_string('myshop.models.{}.smartcard.SmartCard'.format(settings.SHOP_TUTORIAL))
else:
    Product = import_string('myshop.models.polymorphic.product.Product')


class ProductSummarySerializer(ProductSummarySerializerBase):
    media = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'product_url', 'product_type', 'product_model', 'price',
                  'media', 'description')

    def get_media(self, product):
        return self.render_html(product, 'media')

    def get_description(self, product):
        return self.render_html(product, 'description')


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
            product_markedness = product.get_product_markedness(extra.get('product_code'))
        except product.DoesNotExist:
            product_markedness = product.smartphone_set.first()
        instance = {
            'product': product.id,
            'unit_price': product_markedness.unit_price,
            'extra': {'product_code': product_markedness.product_code}
        }
        return instance


class ProductSearchSerializer(ProductSearchSerializerBase):
    """
    Serializer to search over all products in this shop
    """
    app_label = settings.SHOP_APP_LABEL.lower()

    class Meta(ProductSearchSerializerBase.Meta):
        fields = ProductSearchSerializerBase.Meta.fields + ('description', 'media', 'overlay')
        field_aliases = {'q': 'text'}
