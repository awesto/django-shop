# -*- coding: utf-8 -*-
from django.core import exceptions
from django.utils.importlib import import_module
from shop import settings
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
            self._modifiers_list = self._load_modifiers_list()
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

    def _load_modifiers_list(self):
        """
        Heavily inspired by django.core.handlers.base...
        """
        result = []
        for modifier_path in settings.CART_MODIFIERS:
            try:
                mod_module, mod_classname = modifier_path.rsplit('.', 1)
            except ValueError:
                msg = "`{}` isn't a price modifier module"
                raise exceptions.ImproperlyConfigured(msg.format(modifier_path))
            try:
                mod = import_module(mod_module)
            except ImportError, e:
                msg = "Error importing modifier `{}`: {}"
                raise exceptions.ImproperlyConfigured(msg.format(mod_module, e))
            try:
                mod_class = getattr(mod, mod_classname)
            except AttributeError:
                msg = "Price modifier module `{}` does not define a `{}` class"
                raise exceptions.ImproperlyConfigured(msg.format(mod_module, mod_classname))
            mod_instance = mod_class()
            result.append(mod_instance)

        return result

cart_modifiers_pool = CartModifiersPool()
