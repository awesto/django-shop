# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shop.modifiers.base import BaseCartModifier


class ShippingModifier(BaseCartModifier):
    """
    Base class for all shipping modifiers.
    """
    def get_choice(self):
        """
        Returns the tuple used by the shipping forms dialog to display the choice
        """
        raise NotImplemented("Must be implemented by the inheriting class")

    def is_active(self, cart):
        """
        Returns true if this shipping modifier is active.
        """
        return cart.extra.get('shipping_modifier') == self.identifier

    def is_disabled(self, cart):
        """
        Returns True if this shipping modifier is disabled for the current cart.
        Shall be used to temporarily disable a shipping method, if the cart does not
        fulfill certain criteria, such as an undeliverable destination address.
        """
        return False

    def update_render_context(self, context):
        """
        Hook to update the rendering context with shipping specific data.
        """
        from shop.models.cart import CartModel

        if 'shipping_modifiers' not in context:
            context['shipping_modifiers'] = {}
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            if self.is_active(cart):
                cart.update(context['request'])
                data = cart.extra_rows[self.identifier].data
                data.update(modifier=self.identifier)
                context['shipping_modifiers']['initial_row'] = data
        except (KeyError, CartModel.DoesNotExist):
            pass


class SelfCollectionModifier(ShippingModifier):
    """
    This modifiers has not influence on the cart final. It can be used,
    to enable the customer to pick up the products in the shop.
    """
    identifier = 'self-collection'

    def get_choice(self):
        return (self.identifier, _("Self collection"))
