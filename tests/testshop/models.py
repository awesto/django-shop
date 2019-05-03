# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from shop.models.defaults.commodity import Commodity
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.order import Order
from shop.models.order import BaseOrderItem
from shop.models.defaults.delivery import Delivery
from shop.models.defaults.delivery_item import DeliveryItem
from shop.models.defaults.address import BillingAddress, ShippingAddress
from shop.models.defaults.customer import Customer


class OrderItem(BaseOrderItem):
    quantity = models.IntegerField()
    canceled = models.BooleanField(default=False)


__all__ = ['Commodity', 'Cart', 'CartItem', 'Order', 'OrderItem', 'Delivery', 'DeliveryItem',
           'BillingAddress', 'ShippingAddress', 'Customer']
