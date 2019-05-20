# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import MinValueValidator
from django.db.models import IntegerField
from shop.models import cart


class CartItem(cart.BaseCartItem):
    """Default materialized model for CartItem"""
    quantity = IntegerField(validators=[MinValueValidator(0)])
