# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# import default models from djangoSHOP to materialize them
from shop.models.defaults.address import Address
from shop.models.defaults.order import Order
from shop.models.defaults.order_item import OrderItem
from shop.models.defaults.order_shipping import OrderShipping
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.customer import Customer
# models defined by the merchants shop instance itself
from . import smartphone
#from . import commodity
