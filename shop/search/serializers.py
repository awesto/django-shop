# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer


class ProductSearchSerializer(HaystackSerializer):
    """
    The base serializer to represent one or more product fields for beeing returned as a
    result list during searches.
    """
    text = serializers.SerializerMethodField()

    class Meta:
        fields = ('text', 'name', 'product_url',)
        field_aliases = {'q': 'text'}

    def get_text(self, obj):
        pass

    def to_representation(self, instance):
        representation = super(ProductSearchSerializer, self).to_representation(instance)
        representation.pop('text')
        return representation
