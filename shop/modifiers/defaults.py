# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
