from django.utils.translation import gettext_lazy as _

from shop.conf import app_settings
from shop.serializers.cart import ExtraCartRow
from shop.modifiers.base import BaseCartModifier


class CartIncludeTaxModifier(BaseCartModifier):
    """
    This tax calculator presumes that unit prices are net prices, hence also the subtotal,
    and that the tax is added globally to the carts total.
    By placing this modifier after the shipping modifiers, one can add tax to
    the shipping costs. Otherwise shipping cost are considered tax free.
    """
    identifier = 'taxes'
    taxes = app_settings.VALUE_ADDED_TAX / 100

    def add_extra_cart_row(self, cart, request):
        """
        Add a field on cart.extra_price_fields:
        """
        amount = cart.subtotal * self.taxes
        instance = {
            'label': _("plus {}% VAT").format(app_settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount


class CartExcludedTaxModifier(BaseCartModifier):
    """
    This tax calculator presumes that unit prices are gross prices, hence also the subtotal,
    and that the tax is calculated per cart but not added to the cart.
    """
    identifier = 'taxes'
    taxes = 1 - 1 / (1 + app_settings.VALUE_ADDED_TAX / 100)

    def add_extra_cart_row(self, cart, request):
        """
        Add a field on cart.extra_price_fields:
        """
        amount = cart.subtotal * self.taxes
        instance = {
            'label': _("{}% VAT incl.").format(app_settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)

    def add_extra_cart_item_row(self, cart_item, request):
        amount = cart_item.line_total * self.taxes
        instance = {
            'label': _("{}% VAT incl.").format(app_settings.VALUE_ADDED_TAX),
            'amount': amount,
        }
        cart_item.extra_rows[self.identifier] = ExtraCartRow(instance)
