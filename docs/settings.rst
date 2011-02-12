=========
Settings
=========

This is a small list of the settings defined in Django SHOP.

SHOP_PAYMENT_BACKENDS
======================

A list (or iterable) of payment backend class pathes.
These classes will be used as the active payment backends by the checkout system,
and so anything in this list will be shown to the customer for him/her to make
a decision

SHOP_SHIPPING_BACKENDS
=======================

In a similar fashion, this must be a list of Shipping backends. This list is used
to display the end customer what shipping options are available to him/her during 
the checkout process. 

SHOP_CART_MODIFIERS
====================

Theses modifiers function like the django middlewares. The cart will call each of
theses classes, in order, everytime it is displayed. They are passed every item in
the cart, as well as the cart itself.