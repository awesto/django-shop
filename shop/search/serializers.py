# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer


class ProductSearchSerializer(HaystackSerializer):
    """
    The base serializer to represent one or more product fields for being returned as a
    result list during searches.
    """
    text = serializers.SerializerMethodField()  # dummy fields to bypass serialization
    autocomplete = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        fields = ('text', 'autocomplete', 'name', 'product_url', 'price',)

    def get_text(self, obj):
        pass

    def get_autocomplete(self, obj):
        pass

    def get_price(self, search_result):
        """
        The price can't be stored inside the index but must be fetched from the resolved model.
        """
        return search_result.object.get_price(self.context['request'])

    def to_representation(self, instance):
        representation = super(ProductSearchSerializer, self).to_representation(instance)
        representation.pop('text')
        representation.pop('autocomplete')
        return representation
