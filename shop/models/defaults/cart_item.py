# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import MinValueValidator
from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from shop.models import cart


class CartItem(cart.BaseCartItem):
    """Default materialized model for CartItem"""
    quantity = IntegerField(validators=[MinValueValidator(0)])
    extra = JSONField(default={}, verbose_name=_("Arbitrary information for this cart item"))
