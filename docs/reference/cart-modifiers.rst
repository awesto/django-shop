==============
Cart modifiers
==============

Cart modifiers are simple plugins that allow you to define rules in a programmatic way, how the
totals of a cart are computed and how they are labeled. A typical job is to compute tax rates,
adding discounts depending on certain conditions, adding shipping and payment costs, etc.

Instead of implementing each possible combination for all of these use cases, the **djangoSHOP**
framework adds an API, where third party applications can hooks into every computational step.
One thing to note here is that Cart modifiers are not only invoked, when the cart is complete and
the customer wants to proceed to the checkout, but also for each item before being added to the
cart.

This allows the programmer to vary the price of certain items, depending on the current state of
the cart. It can for instance be used, to set one price for the first items added to the cart, and
another price for every further item.

Cart Modifiers are split up into three different categories: Generic, Payment and Shipping. In the
shops ``settings.py`` they must be configured as a list or tuple such as:

.. code-block:: python

	SHOP_CART_MODIFIERS = (
	    'shop.modifiers.defaults.DefaultCartModifier',
	    'shop.modifiers.taxes.CartExcludedTaxModifier',
	    'myshop.modifiers.PostalShippingModifier',
	    'shop.modifiers.defaults.PayInAdvanceModifier',
	    'shop_stripe.modifiers.StripePaymentModifier',
	)

When updating the cart they are applied in the order of the above list. Therefore it can make a
difference, if taxes are applied before or after having applied the shipping costs. Moreover,
some modifiers are applied only under certain conditions.

Cart modifiers are easy to write and they normally consist only of a few lines of code. It is the
intention of this framework to built an eco-system of these kinds of plugins around **djangoSHOP**.

Here is an incomplete list of some useful cart modifiers.


Generic Cart Modifiers
======================

These kinds of cart modifiers are applied unconditionally onto the cart. A typical instance is the
``DefaultCartModifier``, the ``CartIncludeTaxModifier`` or the ``CartExcludeTaxModifier``.


DefaultCartModifier
-------------------


Payment Cart Modifiers
----------------------




How they work
--------------
Cart modifiers should extend the
:class:`shop.modifiers.base.BaseCartModifier` class.

