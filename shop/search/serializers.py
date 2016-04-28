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
        fields = ('text', 'autocomplete', 'product_name', 'product_url', 'price',)
        ignore_fields = ('text', 'autocomplete',)
        field_aliases = {'q': 'text'}

    def get_price(self, search_result):
        """
        The price can't be stored inside the search index but must be fetched from the resolved
        model. In case your product models have a fixed price, try to store it as
        ``indexes.DecimalField`` and retrieve from the search index, because that's much faster.
        """
        if search_result.object:
            return search_result.object.get_price(self.context['request'])
