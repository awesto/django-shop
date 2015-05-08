# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from django.conf import settings

APP_LABEL = settings.SHOP_APP_LABEL  # mandatory setting without default

DEFAULT_CURRENCY = getattr(settings, 'SHOP_DEFAULT_CURRENCY', 'EUR')

MONEY_FORMAT = getattr(settings, 'SHOP_MONEY_FORMAT', '{symbol} {amount}')

DECIMAL_PLACES = getattr(settings, 'SHOP_DECIMAL_PLACES', 2)
"""
Number of decimal places for the internal representation of a price. Not visible to the customer.
"""

CART_MODIFIERS = getattr(settings, 'SHOP_CART_MODIFIERS', ('shop.cart.modifiers.defaults.DefaultCartModifier',))

VALUE_ADDED_TAX = getattr(settings, 'SHOP_VALUE_ADDED_TAX', Decimal('20'))

ORDER_WORKFLOWS = getattr(settings, 'SHOP_ORDER_WORKFLOWS', ())

PAYMENT_WORKFLOWS = getattr(settings, 'SHOP_PAYMENT_WORKFLOWS', ())
