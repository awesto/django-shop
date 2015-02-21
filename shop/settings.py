# -*- coding: utf-8 -*-
from django.conf import settings


DEFAULT_CURRENCY = getattr(settings, 'SHOP_DEFAULT_CURRENCY', 'EUR')

MONEY_FORMAT = getattr(settings, 'SHOP_MONEY_FORMAT', '{symbol} {amount}')

DECIMAL_PLACES = getattr(settings, 'SHOP_DECIMAL_PLACES', 2)
"""
Number of decimal places for the internal representation of a price. Not visible to the customer.
"""
