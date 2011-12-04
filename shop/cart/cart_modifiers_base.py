# -*- coding: utf-8 -*-


class BaseCartModifier(object):
    """
    Price modifiers are the cart's counterpart to backends.
    It allows to implement Taxes and rebates / bulk prices in an elegant
    manner:

    Every time the cart is refreshed (via it's update() method), the cart will
    call all subclasses of this class registered with their full path in the
    settings.SHOP_CART_MODIFIERS setting, calling methods defined here are
    in the following sequence:

    1. pre_process_cart: Totals are not computed, the cart is "rough": only
        relations and quantities are available
    2. process_cart_item: Called for each cart_item in the cart. The current
       total for this item is available as current_total
    (2.a). get_extra_cart_item_price_field: A helper method provided for simple
           use cases. It returns a tuple of (description, value) to add to the
           current cart_item
    3. process_cart: Called once for the whole cart. Here, all fields relative
       to cart items are filled, as well as the cart subtotal. The current
       total is available as Cart.current_total (it includes modifications from
       previous calls to this method, in other modifiers)
    (3.a). get_extra_cart_price_field: A helper method for simple use cases. It
           returns a tuple of (description, value) to add to the current
           cart_item
    4. post_process_cart: all totals are up-to-date, the cart is ready to be
       displayed. Any change you make here must be consistent!
    """

    #==========================================================================
    # Processing hooks
    #==========================================================================

    def pre_process_cart(self, cart, state):
        """
        This method will be called before the cart starts being processed.
        Totals are not updated yet (obviously), but this method can be useful
        to gather some information on products in the cart.

        The `state` parameter is further passed to process_cart_item,
        process_cart, and post_process_cart, so it can be used as a way to
        store per-request arbitrary information.
        """
        pass

    def post_process_cart(self, cart, state):
        """
        This method will be called after the cart was processed.
        The Cart object is "final" and all the fields are computed. Remember
        that anything changed at this point should be consistent: if updating
        the price you should also update all relevant totals (for example).
        """
        pass

    def process_cart_item(self, cart_item, state):
        """
        This will be called for every line item in the Cart:
        Line items typically contain: product, unit_price, quantity...

        Subtotal for every line (unit price * quantity) is already computed,
        but the line total is 0, and is expected to be calculated in the Cart's
        update() method. Subtotal and total should NOT be written by this.

        Overrides of this method should however update cart_item.current_total,
        since it will potentially be used by other modifiers.

        The state parameter is only used to let implementations store temporary
        information to pass between cart_item_modifers and cart_modifiers
        """
        field = self.get_extra_cart_item_price_field(cart_item)
        if field != None:
            price = field[1]
            cart_item.current_total = cart_item.current_total + price
            cart_item.extra_price_fields.append(field)
        return cart_item

    def process_cart(self, cart, state):
        """
        This will be called once per Cart, after every line item was treated
        The subtotal for the cart is already known, but the Total is 0.
        Like for the line items, total is expected to be calculated in the
        cart's update() method.

        Line items should be complete by now, so all of their fields are
        accessible.

        Subtotal is accessible, but total is still 0.0. Overrides are expected
        to update cart.current_total.

        The state parameter is only used to let implementations store temporary
        information to pass between cart_item_modifers and cart_modifiers
        """
        field = self.get_extra_cart_price_field(cart)
        if field != None:
            price = field[1]
            cart.current_total = cart.current_total + price
            cart.extra_price_fields.append(field)
        return cart

    #==========================================================================
    # Simple methods
    #==========================================================================

    def get_extra_cart_item_price_field(self, cart_item):
        """
        Get an extra price field tuple for the current cart_item:

        This allows to modify the price easily, simply return a
        ('Label', Decimal('amount')) from an override. This is expected to be
        a tuple. The decimal should be the amount that should get added to the
        current subtotal. It can be a negative value.

        In case your modifier is based on the current price (for example in
        order to compute value added tax for this cart item only) your
        override can access that price via ``cart_item.current_total``.

        A tax modifier would do something like this:
        >>> return ('taxes', Decimal(9))

        And a rebate modifier would do something along the lines of:
        >>> return ('rebate', Decimal(-9))

        More examples can be found in shop.cart.modifiers.*
        """
        return None  # Does nothing by default

    def get_extra_cart_price_field(self, cart):
        """
        Get an extra price field tuple for the current cart:

        This allows to modify the price easily, simply return a
        ('Label', Decimal('amount')) from an override. This is expected to be
        a tuple. The decimal should be the amount that should get added to the
        current subtotal. It can be a negative value.

        In case your modifier is based on the current price (for example in
        order to compute value added tax for the whole current price) your
        override can access that price via ``cart.current_total``. That is the
        subtotal, updated with all cart modifiers so far)

        >>> return ('Taxes total', 19.00)
        """
        return None
