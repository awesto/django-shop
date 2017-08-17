# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models

from shop.models.fields import ChoiceEnum, ChoiceEnumField
from shop.models.defaults.address import ShippingAddress, BillingAddress
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.customer import Customer
from shop.models.defaults.order import Order
from shop.models.defaults.order_item import OrderItem
from shop.models.defaults.commodity import Commodity


__all__ = ['ShippingAddress', 'BillingAddress', 'Cart', 'CartItem', 'Customer', 'Order', 'OrderItem',
           'Commodity', 'ChoiceEnumFieldTestModel']


class TestChoices(ChoiceEnum):
    OPT_A = 0
    OPT_B = 1


class ChoiceEnumFieldTestModel(models.Model):
    f = ChoiceEnumField(enum_type=TestChoices)

    class Meta:
        app_label = 'tests'
