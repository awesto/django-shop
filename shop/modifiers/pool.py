# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
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
            # check for uniqueness of the modifier's `identifier` attribute
            ModifierException = ImproperlyConfigured("Each modifier requires a unique attribute 'identifier'.")
            try:
                identifiers = [m.identifier for m in self._modifiers_list]
            except AttributeError:
                raise ModifierException
            for i in identifiers:
                if identifiers.count(i) > 1:
                    raise ModifierException
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

    def get_active_shipping_modifier(self, shipping_modifier):
        """
        Return the shipping modifier object for the given string.
        """
        from shop.shipping.modifiers import ShippingModifier

        for modifier in self.get_all_modifiers():
            if isinstance(modifier, ShippingModifier) and modifier.is_active(shipping_modifier):
                return modifier

    def get_active_payment_modifier(self, payment_modifier):
        """
        Return the payment modifier object for the given string.
        """
        from shop.payment.modifiers import PaymentModifier

        for modifier in self.get_all_modifiers():
            if isinstance(modifier, PaymentModifier) and modifier.is_active(payment_modifier):
                return modifier

cart_modifiers_pool = CartModifiersPool()
