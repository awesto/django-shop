========
Tutorial
========

This tutorial is aimed at people new to django-SHOP but already familiar with
django. If you aren't yet, reading their excellent
`django tutorial <https://docs.djangoproject.com/en/1.3/intro/tutorial01/>`_ is
highly recommended.

The steps outlined in this tutorial are meant to be followed in order.

Installation
============

(TODO)

Defining your products
======================

The first thing a shop should do is defining products to sell. While some other
shop solutions do not require you to, in django-SHOP you must write a django
model (or a set of django models) to represent your products.

Roughly, this means you'll need to create a django model subclassing
:class:`shop.models.Product`, add a :class:`Meta` class to it, and
register it with the admin, just like you would do with any other django model.

More information can be found in the :doc:`/howto/how-to-product` section.


Shop rules: cart modifiers
==========================

Cart modifiers are simple python objects that encapsulate all the pricing logic
from your specific shop, such as rebates, taxes, coupons, deals of the week...

Creating a new cart modifier is an easy task: simply create a python object
subclassing :class:`shop.cart.cart_modifiers_base.BaseCartModifier`, and override
either its :meth:`get_extra_cart_item_price_field` or its
:meth:`get_extra_cart_price_field`, depending on whether your "rule" applies to the
whole cart (like taxes for example) or to a single item in your cart (like "buy
two, get one free" rebates).

Theses methods receive either the cart object or the cart item, and need only
return a tuple of the form ``(description, price_difference)``.

More in-depth information can be found in the :doc:`/howto/how-to-cart-mod`
section.


Shipping backends
=================

Payment backends
================

More plugins?
=============

You can find more plugins or share your own plugin with the world on `the
django-SHOP website <https://www.django-shop.org/ecosystem/>`_

Lots of functionality in django-SHOP was left to implement as plugins and
extensions, checking this resource for extra functionality is highly
recommended before starting a new project!
