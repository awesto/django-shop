# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import exceptions

from rest_framework import serializers

from shop.models.customer import CustomerModel
from shop.models.order import OrderItemModel
from shop.rest.money import MoneyField

__all__ = ['BaseCustomerSerializer', 'OrderItemSerializer', 'get_product_summary_serializer_class',
           'set_product_summary_serializer_class']


def get_product_summary_serializer_class():
    """
    Returns the the common ProductSerializer.
    """
    return _product_summary_serializer_class


def set_product_summary_serializer_class(product_summary_serializer_class):
    """
    Sets the common ProductSerializer. This operation can be performed only once.
    """
    global _product_summary_serializer_class

    try:
        _product_summary_serializer_class
    except NameError:
        _product_summary_serializer_class = product_summary_serializer_class
    else:
        msg = "Class `{}` inheriting from `ProductSummarySerializerBase` already registred."
        raise exceptions.ImproperlyConfigured(msg.format(product_summary_serializer_class.__name__))


class BaseCustomerSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='get_number')

    class Meta:
        model = CustomerModel
        fields = ('number', 'first_name', 'last_name', 'email')


class BaseOrderItemSerializer(serializers.ModelSerializer):
    line_total = MoneyField()
    unit_price = MoneyField()

    class Meta:
        model = OrderItemModel
