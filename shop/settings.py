# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings

APP_LABEL = settings.SHOP_APP_LABEL  # mandatory setting without default

DEFAULT_CURRENCY = getattr(settings, 'SHOP_DEFAULT_CURRENCY', 'EUR')

MONEY_FORMAT = getattr(settings, 'SHOP_MONEY_FORMAT', '{symbol} {amount}')

DECIMAL_PLACES = getattr(settings, 'SHOP_DECIMAL_PLACES', 2)
"""
Number of decimal places for the internal representation of a price. Not visible to the customer.
"""

CART_MODIFIERS = getattr(settings, 'SHOP_CART_MODIFIERS', ('shop.cart.modifiers.DefaultCartModifier',))

VALUE_ADDED_TAX = getattr(settings, 'SHOP_VALUE_ADDED_TAX', Decimal('20'))

CUSTOMER_FORM = getattr(settings, 'SHOP_CUSTOMER_FORM', 'shop.forms.checkout.CustomerForm')
SHIPPING_ADDRESS_FORM = getattr(settings, 'SHOP_SHIPPING_ADDRESS_FORM', 'shop.forms.checkout.ShippingAddressForm')
INVOICE_ADDRESS_FORM = getattr(settings, 'SHOP_INVOICE_ADDRESS_FORM', 'shop.forms.checkout.InvoiceAddressForm')
PAYMENT_METHOD_FORM = getattr(settings, 'SHOP_PAYMENT_METHOD_FORM', 'shop.forms.checkout.PaymentMethodForm')
SHIPPING_METHOD_FORM = getattr(settings, 'SHOP_SHIPPING_METHOD_FORM', 'shop.forms.checkout.ShippingMethodForm')
