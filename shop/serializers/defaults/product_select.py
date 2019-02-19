# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.models.product import ProductModel


class ProductSelectSerializer(serializers.ModelSerializer):
    """
    A simple serializer to convert the product's name and code used for rendering the
    `Select2 Widget`_'s content, while looking up for a certain product.
    This serializer shall return a list of 2-tuples, whose 1st entry is the
    primary key of the product and the second entry is the rendered name.

    .. _Select2 Widget: https://github.com/applegrew/django-select2
    """
    text = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ['id', 'text']

    def get_text(self, instance):
        return instance.product_name
