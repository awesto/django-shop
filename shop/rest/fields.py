# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from django.utils import six
from rest_framework import serializers
from shop.money import Money


class OrderedDictField(serializers.Field):
    """
    Serializer field which transparently bypasses the internal representation of an OrderedDict.
    """
    def to_representation(self, obj):
        return OrderedDict(obj)

    def to_internal_value(self, data):
        return OrderedDict(data)


class JSONSerializerField(serializers.Field):
    """
    Serializer field which transparently bypasses its object instead of serializing/deserializing.
    """
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data


class AmountField(serializers.FloatField):
    """
    Serializer field for bidirectional exchange of Money amounts. Internally the serialized
    amount is converted to a float without currency symbol and hence suitable to be used in
    input fields.
    """
    def to_representation(self, obj):
        return float(obj)

    def to_internal_value(self, data):
        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            return Money(data)
        except (TypeError, ValueError):
            self.fail('invalid')
