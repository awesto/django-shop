# -*- coding: utf-8 -*-
from rest_framework import serializers
from shop.models.cart import BaseProduct


class BaseProductSerializer(serializers.ModelSerializer):
    product_url = serializers.CharField(source='get_absolute_url', read_only=True)
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    class Meta:
        model = getattr(BaseProduct, 'MaterializedModel')
        fields = ('name', 'identifier', 'product_url', 'price', 'availability',) + getattr(model, 'serialize_fields', ())

    def get_price(self, obj):
        return obj.get_price(self.context['request'])

    def get_availability(self, obj):
        return obj.get_availability(self.context['request'])
