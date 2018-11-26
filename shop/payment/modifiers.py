# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shop.modifiers.base import BaseCartModifier
from shop.payment.providers import ForwardFundPayment


class PaymentModifier(BaseCartModifier):
    """
    Base class for all payment modifiers.
    """
    def get_choice(self):
        """
        Returns the tuple used by the payment forms dialog to display the choice.
        """
        raise NotImplemented("Must be implemented by the inheriting class")

    def is_active(self, cart):
        """
        Returns true if this payment modifier is active.
        """
        assert hasattr(self, 'payment_provider'), "A Payment Modifier requires a Payment Provider"
        return cart.extra.get('payment_modifier') == self.payment_provider.namespace

    def is_disabled(self, cart):
        """
        Returns True if this payment modifier is disabled for the current cart.
        Shall be used to temporarily disable a payment method, if the cart does not
        fulfill certain criteria, such as a minimum total.
        """
        return False

    def update_render_context(self, context):
        """
        Hook to update the rendering context with payment specific data.
        """
        from shop.models.cart import CartModel

        if 'payment_modifiers' not in context:
            context['payment_modifiers'] = {}
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            if self.is_active(cart):
                cart.update(context['request'])
                data = cart.extra_rows[self.identifier].data
                data.update(modifier=self.identifier)
                context['payment_modifiers']['initial_row'] = data
        except (KeyError, CartModel.DoesNotExist):
            pass


class PayInAdvanceModifier(PaymentModifier):
    """
    This modifiers has no influence on the cart final. It can be used,
    to enable the customer to pay the products on delivery.
    """
    identifier = 'pay-in-advance'
    payment_provider = ForwardFundPayment()

    def get_choice(self):
        return (self.identifier, _("Pay in advance"))
