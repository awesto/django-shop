# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.conf import app_settings
from .base import ShippingModifier, PaymentModifier


class CartModifiersPool(object):

    USE_CACHE = True

    def __init__(self):
        self._modifiers_list = []

    def get_all_modifiers(self):
        """
        Returns all registered modifiers of this shop instance.
        """
        if not self.USE_CACHE or not self._modifiers_list:
            self._modifiers_list = [mc() for mc in app_settings.CART_MODIFIERS]
        return self._modifiers_list

    def get_shipping_modifiers(self):
        """
        Returns all registered shipping modifiers of this shop instance.
        """
        return [m for m in self.get_all_modifiers() if isinstance(m, ShippingModifier)]

    def get_payment_modifiers(self):
        """
        Returns all registered payment modifiers of this shop instance.
        """
        return [m for m in self.get_all_modifiers() if isinstance(m, PaymentModifier)]

cart_modifiers_pool = CartModifiersPool()
