==============================
How to create a Cart modifier
==============================

Cart modifiers are simple plugins that allow you to define rules according to
which carts should be modified (and in what order).

Generally, this is how you implement a "bulk rebate" module, for instance.

Writing a simple cart modifier for the whole cart
==================================================

Let's assume you want to provide a discount of 10% off the cart's total to
clients that buy more than 500$ of goods.

This will affect the price of the whole cart. We will therefore override the
:meth:`get_extra_cart_price_field` method of
:class:`shop.cart.cart_modifiers_base.BaseCartModifier`::

    from shop.cart.cart_modifiers_base import BaseCartModifier
    from decimal import Decimal # We need this because python's float are confusing
    
    class MyModifier(BaseCartModifier):
        """
        An example class that will grant a 10% discount to shoppers who buy
        more than 500 worth of goods.
        """
        def get_extra_cart_price_field(self, cart):
            ten_percent = Decimal('10') / Decimal('100')
            # Now we need the current cart total. It's not just the subtotal field
            # because there may be other modifiers before this one
            total = cart.current_total
            
            if total > Decimal('500'):
                rebate_amount = total * ten_percent
                rebate_amount = - rebate_amount # a rebate is a negative difference
                return ('My awesome rebate', rebate_amount)
            else:
                return None # None is no-op: it means "do nothing"
            
Adding this cart modifier to your SHOP_CART_MODIFIERS setting will enable it, and
you should be able to already test that your cart displays a rebate when the 
total for the order is over 500.


.. note::
   When using ``cart.extra_price_fields.append('your label', price)`` you might
   want to use ``from django.utils.translation import ugettext as _`` for your
   label in multilingual projects. Please make sure that you use ``gettext``
