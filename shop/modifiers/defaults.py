# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

from shop.modifiers.base import PaymentModifier, ShippingModifier
from shop.money import AbstractMoney, Money
from shop.payment.defaults import ForwardFundPayment
from shop.shipping.defaults import DefaultShippingProvider
from .base import BaseCartModifier


class DefaultCartModifier(BaseCartModifier):
    """
    This modifier is required for almost every shopping cart. It handles the most basic
    calculations, ie. multiplying the items unit prices with the chosen quantity.
    Since this modifier sets the cart items line total, it must be listed as the first
    entry in `SHOP_CART_MODIFIERS`.
    """
    def process_cart_item(self, cart_item, request):
        cart_item.unit_price = cart_item.product.get_price(request)
        cart_item.line_total = cart_item.unit_price * cart_item.quantity
        return super(DefaultCartModifier, self).process_cart_item(cart_item, request)

    def process_cart(self, cart, request):
        if not isinstance(cart.subtotal, AbstractMoney):
            # if we don't know the currency, use the default
            cart.subtotal = Money(cart.subtotal)
        cart.total = cart.subtotal
        return super(DefaultCartModifier, self).process_cart(cart, request)


class WeightedCartModifier(BaseCartModifier):
    """
    This modifier is required for all shopping cart where we are interested into its weight.
    It sums up the weight of all articles, ie. multiplying the items weight with the chosen
    quantity.
    If this modifier is used, the classes implementing the product shall override their
    method ``get_weight()``, which must return the weight in kg as Decimal type.
    """
    def pre_process_cart(self, cart, request):
        cart.weight = Decimal(0)
        return super(WeightedCartModifier, self).process_cart(cart, request)

    def pre_process_cart_item(self, cart, cart_item, request):
        cart.weight += Decimal(cart_item.product.get_weight() * cart_item.quantity)
        return super(WeightedCartModifier, self).process_cart_item(cart_item, request)


class PayInAdvanceModifier(PaymentModifier):
    """
    This modifiers has no influence on the cart final. It can be used,
    to enable the customer to pay the products on delivery.
    """
    identifier = 'pay-in-advance'
    payment_provider = ForwardFundPayment()

    def get_choice(self):
        return (self.identifier, _("Pay in advance"))


class SelfCollectionModifier(ShippingModifier):
    """
    This modifiers has not influence on the cart final. It can be used,
    to enable the customer to pick up the products in the shop.
    """
    identifier = 'self-collection'
    shipping_provider = DefaultShippingProvider()

    def get_choice(self):
        return (self.identifier, _("Self collection"))
