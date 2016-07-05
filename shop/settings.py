# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings

APP_LABEL = settings.SHOP_APP_LABEL  # mandatory setting without default

DEFAULT_CURRENCY = getattr(settings, 'SHOP_DEFAULT_CURRENCY', 'EUR')

MONEY_FORMAT = getattr(settings, 'SHOP_MONEY_FORMAT', '{symbol} {amount}')
"""
When rendering an amount of type Money, use this format. Possible placeholders are:
{symbol}: This can be €, $, £, etc.
{currency}: This can be EUR, USD, GBP, etc.
{amount}: The localized amount .
"""

USE_TZ = True

DECIMAL_PLACES = getattr(settings, 'SHOP_DECIMAL_PLACES', 2)
"""
Number of decimal places for the internal representation of a price. Not visible to the customer.
"""

CART_MODIFIERS = getattr(settings, 'SHOP_CART_MODIFIERS', ('shop.modifiers.defaults.DefaultCartModifier',))

VALUE_ADDED_TAX = getattr(settings, 'SHOP_VALUE_ADDED_TAX', Decimal('20'))

ORDER_WORKFLOWS = getattr(settings, 'SHOP_ORDER_WORKFLOWS', ())

ADD2CART_NG_MODEL_OPTIONS = getattr(settings, 'SHOP_ADD2CART_NG_MODEL_OPTIONS', "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")
EDITCART_NG_MODEL_OPTIONS = getattr(settings, 'SHOP_EDITCART_NG_MODEL_OPTIONS', "{updateOn: 'default blur', debounce: {'default': 500, 'blur': 0}}")
"""
Use ``SHOP_EDITCART_NG_MODEL_OPTIONS`` and ``SHOP_ADD2CART_NG_MODEL_OPTIONS`` to configure the
update behavior when changing the quantity of a cart item. For more information refer to the
AngularJS docs: https://code.angularjs.org/1.3.7/docs/api/ng/directive/ngModelOptions
"""

GUEST_IS_ACTIVE_USER = getattr(settings, 'SHOP_GUEST_IS_ACTIVE_USER', False)
"""
If ``SHOP_GUEST_IS_ACTIVE_USER`` is True, Customers which declared themselves as guests, may request
a password reset, so that they can log into their account at a later time. The default is False.
"""

CACHE_DURATIONS = {
    'product_html_snippet': 86400,
}
CACHE_DURATIONS.update(getattr(settings, 'SHOP_CACHE_DURATIONS', {}))
