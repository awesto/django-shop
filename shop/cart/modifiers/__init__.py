# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import BaseCartModifier


class DefaultCartModifier(BaseCartModifier):
    """
    This modifier is required for almost every shopping cart. It handles the most basic
    calculations, ie. multiplying the items unit prices with the chosen quantity.
    Since this modifier sets the cart items line total, it must be listed as the first
    entry in `SHOP_CART_MODIFIERS`.
    """
    def process_cart_item(self, cart_item, request):
        cart_item.line_total = cart_item.product.get_price(request) * cart_item.quantity
        return super(DefaultCartModifier, self).process_cart_item(cart_item, request)

    def process_cart(self, cart, request):
        cart.total = cart.subtotal
        return super(DefaultCartModifier, self).process_cart(cart, request)
