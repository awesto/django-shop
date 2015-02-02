# -*- coding: utf-8 -*-
from rest_framework import serializers
from shop.models.cart import BaseCart, BaseCartItem


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = getattr(BaseCart, 'MaterializedModel')
        fields = ('user',)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = getattr(BaseCartItem, 'MaterializedModel')
        fields = ('quantity', 'product',)
