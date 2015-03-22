# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models import cart


class CartItem(cart.BaseCartItem):
    """Default materialized model for CartItem"""
