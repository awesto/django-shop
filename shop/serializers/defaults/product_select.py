# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.models.product import ProductModel


class ProductSelectSerializer(serializers.ModelSerializer):
    """
    A simple serializer to convert the product's name and code for while rendering the `Select2 Widget`_
    when looking up for a product. This serializer shall return a list of 2-tuples, whose 1st entry is the
    primary key of the product and the second entry is the rendered name.

    .. _Select2 Widget: https://github.com/applegrew/django-select2
    """
    text = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ['id', 'text']

    def get_text(self, instance):
        return instance.product_name
