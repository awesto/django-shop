# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.conf import app_settings
from shop.models.delivery import DeliveryModel, DeliveryItemModel
from shop.modifiers.pool import cart_modifiers_pool


class DeliveryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryItemModel
        exclude = ['id', 'delivery', 'item']

    def to_representation(self, instance):
        data = app_settings.ORDER_ITEM_SERIALIZER(instance.item, context=self.context).data
        data['ordered_quantity'] = data.pop('quantity', None)
        data.update(super(DeliveryItemSerializer, self).to_representation(instance))
        return data


class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(
        many=True,
        read_only=True,
    )

    shipping_method = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryModel
        exclude = ['id', 'order']

    def get_shipping_method(self, instance):
        for shipping_modifier in cart_modifiers_pool.get_shipping_modifiers():
            identifier, label = shipping_modifier.get_choice()
            if identifier == shipping_modifier.identifier:
                return label
        return instance.shipping_method
