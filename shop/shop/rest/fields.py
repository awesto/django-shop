from collections import OrderedDict
from rest_framework import serializers


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
    def __init__(self, encoder=None, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data
