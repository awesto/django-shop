# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models import cart


class Cart(cart.BaseCart):
    """Default materialized model for Cart"""


class CartItem(cart.BaseCartItem):
    """Default materialized model for CartItem"""
