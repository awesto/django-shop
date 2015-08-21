# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseCartModifier(object):
    """
    Price modifiers are the cart's counterpart to backends.
    It allows to implement Taxes and rebates / bulk prices in an elegant manner:

    Every time the cart is refreshed (via it's update() method), the cart will call all subclasses
    of this modifier class registered with their full path in `settings.SHOP_CART_MODIFIERS`.

    The methods defined here are called in the following sequence:

    1.  `pre_process_cart`: Totals are not computed, the cart is "rough": only relations and
        quantities are available
    2.  `process_cart_item`: Called for each cart_item in the cart. The modifier may change the
        amount in `cart_item.line_total`.
    2a. `add_extra_cart_item_row`: It optionally adds an object of type `ExtraCartRow` to the
        current cart item. This object adds additional information displayed on each cart items
        line.
    3.  `process_cart`: Called once for the whole cart. Here, all fields relative to cart items are
        filled. Here the carts subtotal is used to computer the carts total.
    3a. `add_extra_cart_row`: It optionally adds an object of type `ExtraCartRow` to the current
        cart. This object adds additional information displayed in the carts footer section.
    4.  `post_process_cart`: all totals are up-to-date, the cart is ready to be displayed. Any
        change you make here must be consistent!
    Each method accepts the HTTP `request` object. It shall be used to let implementations
    determine their prices according to the session, and other request information. The `request`
    object also can be used to store arbitrary data to be passed between modifers using the
    temporary dict `request.cart_modifiers_state`.
    """

    def __init__(self, identifier=None):
        """
        Initialize the modifier with a named identifier. Defaults to its classname.
        """
        self.identifier = identifier or getattr(self, 'identifier', self.__class__.__name__.lower())

    def pre_process_cart(self, cart, cart_items, request):
        """
        This method will be called before the Cart starts being processed.
        Totals are not updated yet, but this method can be useful to gather some information
        on products, modify the cart and its items via the extra dictionaries, and to reorder
        the cart items if necessary.
        """
        return cart_items

    def post_process_cart(self, cart, request):
        """
        This method will be called after the cart was processed in reverse order of the
        registered cart modifiers.
        The Cart object is "final" and all the fields are computed. Remember that anything changed
        at this point should be consistent: If updating the price you should also update all
        relevant totals (for example).
        """
        pass

    def process_cart_item(self, cart_item, request):
        """
        This will be called for every line item in the Cart:
        Line items typically contain: product, unit_price, quantity and optional extra row
        information.

        If configured, the starting line total for every line (unit price * quantity) is computed
        by the `DefaultCartModifier`, which typically is listed as the first modifier. Posterior
        modifiers can optionally change the cart items line total.

        After processing all cart items with all modifiers, these line totals are summed up to form
        the carts subtotal, which is used by method `process_cart`.
        """
        self.add_extra_cart_item_row(cart_item, request)

    def process_cart(self, cart, request):
        """
        This will be called once per Cart, after every line item was treated by method
        `process_cart_item`.

        The subtotal for the cart is already known, but the total is still unknown.
        Like for the line items, the total is expected to be calculated by the first cart modifier,
        which typically is the `DefaultCartModifier`. Posterior modifiers can optionally change the
        total and add additional information to the cart using an object of type `ExtraCartRow`.
        """
        self.add_extra_cart_row(cart, request)

    def add_extra_cart_item_row(self, cart_item, request):
        """
        Optionally add an `ExtraCartRow` object to the current cart item.

        This allows to add an additional row description to a cart item line.
        This method optionally utilizes or modifies the amount in `cart_item.line_total`.
        """

    def add_extra_cart_row(self, cart, request):
        """
        Optionally add an `ExtraCartRow` object to the current cart.

        This allows to add an additional row description to the cart.
        This method optionally utilizes `cart.subtotal` and modifies the amount in `cart.total`.
        """


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
        return cart.extra.get('payment_modifier') == self.identifier

    def update_render_context(self, context):
        """
        Hook to update the rendering context with payment specific data.
        """
        if 'payment_modifiers' not in context:
            context['payment_modifiers'] = {}


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

    def update_render_context(self, context):
        """
        Hook to update the rendering context with shipping specific data.
        """
        if 'shipping_modifiers' not in context:
            context['shipping_modifiers'] = {}
