from django.utils.translation import gettext_lazy as _

from shop.modifiers.base import BaseCartModifier
from shop.payment.providers import PaymentProvider, ForwardFundPayment


class PaymentModifier(BaseCartModifier):
    """
    Base class for all payment modifiers. The purpose of a payment modifier is to calculate the payment surcharge and/or
    prevent its usage, in case the choosen payment method is not available for the given customer. The merchant may
    either append a single payment modifier to the list of ``SHOP_CART_MODIFIERS``, or create a sublist of payment
    modifier and append this sublist to ``SHOP_CART_MODIFIERS``. The latter is useful to instantiate the same payment
    modifier multiple times for different payment service providers using the same interface.

    The merchant must specify at least one payment modifier. If there is more than one, the merchant shall offer a
    select option during checkout. In django-SHOP, one can use the plugin **Payment Method Form** to render such a
    select option.

    Each payment modifier can add a surcharge on the current cart.
    """
    def __init__(self):
        assert isinstance(getattr(self, 'payment_provider', None), PaymentProvider), \
            "Each Payment modifier class requires a Payment Provider"
        super().__init__()

    @property
    def identifier(self):
        """
        Default identifier for payment providers.
        """
        return self.payment_provider.namespace

    def get_choice(self):
        """
        :returns: A tuple consisting of 'value, label' used by the payment form dialog to render
        the available payment choices.
        """
        raise NotImplemented("{} must implement method `get_choice()`.".format(self.__class__))

    def is_active(self, payment_modifier):
        """
        :returns: ``True`` if this payment modifier is active.
        """
        assert hasattr(self, 'payment_provider'), "A Payment Modifier requires a Payment Provider"
        return payment_modifier == self.identifier

    def is_disabled(self, cart):
        """
        Hook method to be overridden by the concrete payment modifier. Shall be used to
        temporarily disable a payment method, in case the cart does not fulfill certain criteria,
        for instance a too small total.

        :returns: ``True`` if this payment modifier is disabled for the current cart.
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
            if self.is_active(cart.extra.get('payment_modifier')):
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
    payment_provider = ForwardFundPayment()

    def get_choice(self):
        return (self.payment_provider.namespace, _("Pay in advance"))
