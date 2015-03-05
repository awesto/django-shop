# -*- coding: utf-8 -*-
from django.utils.translation import ugettext
from shop import settings
from shop.rest.serializers import ExtraCartRow
from shop.cart.modifiers.base import BaseCartModifier


class CartIncludeTaxModifier(BaseCartModifier):
    """
    This tax calculator presumes that unit prices are net prices, hence also the subtotal,
    and that the tax is added globally to the carts total.
    By placing this modifier before the shipping modifiers, one can add tax to
    the shipping costs. Otherwise shipping cost are considered tax free.
    """
    taxes = settings.VALUE_ADDED_TAX / 100

    def add_extra_cart_row(self, cart, request):
        """
        Add a field on cart.extra_price_fields:
        """
        amount = cart.subtotal * self.taxes
        instance = {
            'label': ugettext("+ {}% V.A.T").format(settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount


class CartExcludedTaxModifier(BaseCartModifier):
    """
    This tax calculator presumes that unit prices are gross prices, hence also the subtotal,
    and that the tax is identified per cart but not added.
    """
    taxes = 1 - 1 / (1 + settings.VALUE_ADDED_TAX / 100)

    def add_extra_cart_row(self, cart, request):
        """
        Add a field on cart.extra_price_fields:
        """
        amount = cart.subtotal * self.taxes
        instance = {
            'label': ugettext("{}% V.A.T incl.").format(settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
