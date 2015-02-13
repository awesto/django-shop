# -*- coding: utf-8 -*-
from rest_framework import serializers
from shop.models.cart import BaseProduct


class BaseProductSerializer(serializers.ModelSerializer):
    product_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = getattr(BaseProduct, 'MaterializedModel')
        fields = ('product_url',) + model.serialize_fields
