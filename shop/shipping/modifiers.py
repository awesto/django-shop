from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from shop.modifiers.base import BaseCartModifier


class ShippingModifier(BaseCartModifier):
    """
    Base class for all shipping modifiers. The purpose of a shipping modifier is to calculate the shipping costs and/or
    prevent its usage, in case products in the cart can not be shipped to the desired destination. The merchant may
    either append a single shipping modifier to the list of ``SHOP_CART_MODIFIERS``, or create a sublist of shipping
    modifier and append this sublist to ``SHOP_CART_MODIFIERS``. The latter is useful to instantiate the same shipping
    modifier multiple times for different shipping carriers using the same interface.

    The merchant must specify at least one shipping modifier. If there is more than one, the merchant shall offer a
    select option during checkout. In django-SHOP, one can use the plugin **Shipping Method Form** to render such a
    select option.

    Each shipping modifier can add a surcharge on the current cart. If weight affects the shipping price, it shall be
    summed up inside the method `add_extra_cart_row` and used to lookup the shipping costs.
    """
    def get_choice(self):
        """
        :returns: A tuple consisting of 'value, label' used by the shipping form dialog to render
        the available shipping choices.
        """
        raise NotImplemented("{} must implement method `get_choice()`.".format(self.__class__))

    def is_active(self, shipping_modifier):
        """
        :returns: ``True`` if this shipping modifier is the actively selected one.
        """
        return shipping_modifier == self.identifier

    def is_disabled(self, cart):
        """
        Hook method to be overridden by the concrete shipping modifier. Shall be used to
        temporarily disable a shipping method, in case the cart does not fulfill certain criteria,
        for instance an undeliverable destination address.

        :returns: ``True`` if this shipping modifier is disabled for the current cart.
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
            if self.is_active(cart.extra.get('shipping_modifier')):
                cart.update(context['request'])
                data = cart.extra_rows[self.identifier].data
                data.update(modifier=self.identifier)
                context['shipping_modifiers']['initial_row'] = data
        except (KeyError, CartModel.DoesNotExist):
            pass

    def ship_the_goods(self, delivery):
        """
        Hook to be overridden by the active shipping modifier. It should be used to perform the
        shipping request.
        """
        delivery.shipped_at = timezone.now()


class SelfCollectionModifier(ShippingModifier):
    """
    This modifiers has not influence on the cart final. It can be used,
    to enable the customer to pick up the products in the shop.
    """
    identifier = 'self-collection'

    def get_choice(self):
        return (self.identifier, _("Self-collection"))

    def ship_the_goods(self, delivery):
        if not delivery.shipping_id:
            delivery.shipping_id = str(delivery.id)
        super().ship_the_goods(delivery)
