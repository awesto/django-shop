==============
Cart modifiers
==============

Cart Modifiers are simple plugins that allow you to define rules in a programmatic way, how the
totals of a cart are computed and how they are labeled. A typical job is to compute tax rates,
adding discounts, shipping and payment costs, etc.

Instead of implementing each possible combination for all of these use cases, the **djangoSHOP**
framework offers an API, where third party applications can hooks into every computational step.
One thing to note here is that Cart Modifiers are not only invoked, when the cart is complete and
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

When updating the cart, these modifiers are applied in the order of the above list. Therefore it
makes a difference, if taxes are applied before or after having applied the shipping costs.

Moreover, whenever in the detail view the quantity of a product is updated, then all configured
modifiers are ran for that item. This allows the ``ItemModelSerializer``, to even change the unit
price of product depending on the total content of the cart.

Cart modifiers are easy to write and they normally consist only of a few lines of code. It is the
intention of **djangoSHOP** to seed an eco-system for these kinds of plugins.

Here is an incomplete list of some useful cart modifiers.


Generic Cart Modifiers
======================

These kinds of cart modifiers are applied unconditionally onto the cart. A typical instance is the
``DefaultCartModifier``, the ``CartIncludeTaxModifier`` or the ``CartExcludeTaxModifier``.


DefaultCartModifier
-------------------

The :class:DefaultCartModifier_ is required for almost every shopping cart. It handles the most
basic calculations, ie. multiplying the items unit prices with the chosen quantity.
Since this modifier sets the cart items line total, it must be listed as the first entry in
``SHOP_CART_MODIFIERS``.


Payment Cart Modifiers
----------------------

From these kinds of modifiers, only that for the chosen payment method is applied. Payment Modifiers
are used to add extra costs or discounts depending on the chosen payment method. By overriding the
method ``is_disabled`` a payment method can be disabled; useful to disable certain payments in case
the carts total is below a certain threshold.


Shipping Cart Modifiers
-----------------------

From these kinds of modifiers, only that for the chosen shipping method is applied. Shipping
Modifiers are used to add extra costs or discounts depending on chosen shipping method, the number
of items in the cart and their weight. By overriding the method ``is_disabled`` a shipping method
can be disabled; useful to disable certain payments in case the carts total is below a certain
threshold.


How Modifiers work
------------------
Cart modifiers should extend the :class:`shop.modifiers.base.BaseCartModifier` class and extend one
or more of the given methods:

.. note:: Until version 0.2 of **djangoSHOP**, the Cart Modifiers returned the amount and label
		for the extra item rows, and **djangoSHOP** added them up. Since Version 0.3 cart modifiers
		must change the line subtotals and cart total themselves.

.. autoclass:: shop.modifiers.base.BaseCartModifier
   :members:
