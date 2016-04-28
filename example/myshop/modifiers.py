# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from shop.modifiers.pool import cart_modifiers_pool
from shop.rest.serializers import ExtraCartRow
from shop.modifiers.base import ShippingModifier
from shop.money import Money
from shop.shipping.defaults import DefaultShippingProvider
from shop_stripe import modifiers


class PostalShippingModifier(ShippingModifier):
    identifier = 'postal-shipping'
    shipping_provider = DefaultShippingProvider()

    def get_choice(self):
        return (self.identifier, _("Postal shipping"))

    def add_extra_cart_row(self, cart, request):
        if not self.is_active(cart) and len(cart_modifiers_pool.get_shipping_modifiers()) > 1:
            return
        # add a shipping flat fee
        amount = Money('5')
        instance = {'label': _("Shipping costs"), 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount


class CustomerPickupModifier(ShippingModifier):
    identifier = 'customer-pickup'

    def get_choice(self):
        return (self.identifier, _("Customer pickups the goods"))


class StripePaymentModifier(modifiers.StripePaymentModifier):
    commision_percentage = 3
