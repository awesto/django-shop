# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.modifiers.defaults import DefaultCartModifier
from myshop.models.polymorphic.smartphone import SmartPhoneModel


class MyShopCartModifier(DefaultCartModifier):
    """
    Extended default cart modifier which handles the price for product variations
    """
    def process_cart_item(self, cart_item, request):
        if isinstance(cart_item.product, SmartPhoneModel):
            product_code = cart_item.extra.get('product_code')
            cart_item.unit_price = cart_item.product.get_product_variant(product_code).unit_price
        else:
            cart_item.unit_price = cart_item.product.get_price(request)
        cart_item.line_total = cart_item.unit_price * cart_item.quantity
        # grandparent super
        return super(DefaultCartModifier, self).process_cart_item(cart_item, request)
