# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.fields import empty

from shop.serializers.bases import ProductSerializer
from shop.serializers.defaults import AddToCartSerializer

from myshop.models import SmartCard, SmartPhoneModel


class SmartCardSerializer(ProductSerializer):
    class Meta:
        model = SmartCard
        fields = ['product_name', 'slug', 'unit_price', 'manufacturer', 'card_type', 'speed',
                  'product_code', 'storage']


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


class SmartPhoneSerializer(ProductSerializer):
    class Meta:
        model = SmartPhoneModel
        fields = ['product_name', 'slug', 'battery_type', 'battery_capacity']


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
