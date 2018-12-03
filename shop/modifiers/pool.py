# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.conf import app_settings


class CartModifiersPool(object):

    USE_CACHE = True

    def __init__(self):
        self._modifiers_list = []

    def get_all_modifiers(self):
        """
        Returns all registered modifiers of this shop instance.
        """
        if not self.USE_CACHE or not self._modifiers_list:
            self._modifiers_list = []
            for modifiers_class in app_settings.CART_MODIFIERS:
                if issubclass(modifiers_class, (list, tuple)):
                    self._modifiers_list.extend([mc() for mc in modifiers_class()])
                else:
                    self._modifiers_list.append(modifiers_class())
            # TODO: check for unique identifiers
        return self._modifiers_list

    def get_shipping_modifiers(self):
        """
        Returns all registered shipping modifiers of this shop instance.
        """
        from shop.shipping.modifiers import ShippingModifier

        return [m for m in self.get_all_modifiers() if isinstance(m, ShippingModifier)]

    def get_payment_modifiers(self):
        """
        Returns all registered payment modifiers of this shop instance.
        """
        from shop.payment.modifiers import PaymentModifier

        return [m for m in self.get_all_modifiers() if isinstance(m, PaymentModifier)]

cart_modifiers_pool = CartModifiersPool()
