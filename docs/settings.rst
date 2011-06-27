================
General Settings
================

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

SHOP_ADDRESS_MODEL
===================
(Optional)
When defined, should be the full python path to the Model to use as an Address model
in the checkout process.


==========================
Backend specific Settings
==========================

Some backends define extra settings to tweak their behavior. This should be an
exhaustive list of all of the backends and modifiers included in the trunk of
django SHOP.

SHOP_SHIPPING_FLAT_RATE
========================

The "flat rate" shipping module uses this to know how much to charge. This
should be a string, and will be converted to a Decimal by the backend. 

=======================
Extensibility Settings
=======================

Theses settings allow developers to extend the shop's functionality by replacing
models by their own models. More information about how to use theses settings 
can be found in the :doc:`/howto/how-to-extend-django-shop-models` section.

SHOP_CART_MODEL
================
(Optional)
A python classpath to the class you want to replace the Cart model with.
Example value: `myproject.models.MyCartModel`

SHOP_ADDRESS_MODEL
================
(Optional)
A python classpath to the class you want to replace the Address model with.
See :doc:`/howto/how-to-use-your-own-clientmodel` for a more complete example.
Example value: `myproject.models.MyAddressModel`

SHOP_ORDER_MODEL
================
(Optional)
A python classpath to the class you want to replace the Oredr model with.
Example value: `myproject.models.MyOrderModel`