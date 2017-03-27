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
        if data is empty:
            product_code = None
            extra = {}
        else:
            product_code = data.get('product_code')
            extra = data.get('extra', {})
        try:
            variant = product.get_product_variant(product_code=product_code)
        except product.DoesNotExist:
            variant = product.smartphone_set.first()
        extra.update(storage=variant.storage)
        instance = {
            'product': product.id,
            'product_code': variant.product_code,
            'unit_price': variant.unit_price,
            'extra': extra,
        }
        return instance
