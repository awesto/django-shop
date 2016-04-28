# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from shop import settings
from shop.rest.serializers import ExtraCartRow
from .base import BaseCartModifier


class CartIncludeTaxModifier(BaseCartModifier):
    """
    This tax calculator presumes that unit prices are net prices, hence also the subtotal,
    and that the tax is added globally to the carts total.
    By placing this modifier after the shipping modifiers, one can add tax to
    the shipping costs. Otherwise shipping cost are considered tax free.
    """
    taxes = settings.VALUE_ADDED_TAX / 100

    def add_extra_cart_row(self, cart, request):
        """
        Add a field on cart.extra_price_fields:
        """
        amount = cart.subtotal * self.taxes
        instance = {
            'label': _("plus {}% VAT").format(settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount


class CartExcludedTaxModifier(BaseCartModifier):
    """
    This tax calculator presumes that unit prices are gross prices, hence also the subtotal,
    and that the tax is calculated per cart but not added to the cart.
    """
    taxes = 1 - 1 / (1 + settings.VALUE_ADDED_TAX / 100)

    def add_extra_cart_row(self, cart, request):
        """
        Add a field on cart.extra_price_fields:
        """
        amount = cart.subtotal * self.taxes
        instance = {
            'label': _("{}% VAT incl.").format(settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
