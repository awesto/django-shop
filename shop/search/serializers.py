# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer


class ProductSearchSerializer(HaystackSerializer):
    """
    The base serializer to represent one or more product fields for being returned as a
    result list during searches.
    """
    price = serializers.SerializerMethodField()

    class Meta:
        fields = ('text', 'autocomplete', 'name', 'product_url', 'price', 'media')
        ignore_fields = ('text', 'autocomplete',)

    def get_price(self, search_result):
        """
        The price can't be stored inside the search index but must be fetched from the resolved
        model. In case your product models have fixed prices, try to store and retrieve them
        from the search index, because that's much faster.
        """
        if search_result.object:
            return search_result.object.get_price(self.context['request'])

    def to_representation(self, instance):
        representation = super(ProductSearchSerializer, self).to_representation(instance)
        return representation
