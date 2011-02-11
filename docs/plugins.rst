================
Plugins
================

Django Shop defines 3 types of different plugins for the time being:
1. Cart modifiers
2. Shipping modules
3. Payment modules

Cart modifiers
===============

Cart modifiers are plugins that modify the cart's contents.
Rough categories could be discount modules or tax modules: rules for theses modules
are invariant, and should be "stacked".
Example: "CDs are buy two get one free this month", "orders over 500$ get a 10% 
discount"

How they work
--------------
Cart modifiers should extend the shop.cart.cart_modifiers_base.BaseCartModifier
class.

Users must register theses filters in the settings.SHOP_PRICE_MODIFIERS settings 
entry. Modifiers will be iterated and function in the same fashion as django 
middleware classes.

BaseCartModifier defines a set of methods that implementations should override, and that
are called for each cart item/cart when the cart's update() method is called.
 
Example implementations
------------------------
You can refer to shop.cart.modifiers.* package to see some example implementations


Shipping backends
==================

Shipping backends differ from price modifiers in that there must be only one
shipping backend selected per Order (the shopper must choose which delivery method
to use)

Shipping costs should be calculated on an Order Object, not on a Cart object (Orders
are fully serialized in the database for archiving purposes).

How they work
--------------

Shipping backends need to subclass 
shop.shipping.shipping_backend_base.BaseShippingBackend, and be registered in 
the SHOP_SHIPPING_BACKENDS Django setting.

Extending this class allows the backend to expose a set of functions, and to 
access the shop system's interface via ``self.shop``.

The core functionality the shop exposes is the ability to retrieve the current 
Order object (and all it's related bits and pieces such as extra price fields,
line items etc...) via a convenient self.shop.get_order() call. This allows for
your module to be reused relatively easily should another shop system implement
this interface.

On their part, shipping backends should expose at least a get_urls() method,
returning a urlpattern-style list or urls. This allows backend writers to have
almost full control of the shipping process (they can create views and make them
available to the URL resolver).

Please note that module URLs should be namespaced, and will be added to the 
``ship/`` URL namespace. This is a hard limitation to avoid URL name clashes.


Payment backends
=================

Payment backends must also be selected by the end user (the shopper).
Theses modules take care of the actual payment processing.

How they work
--------------

Similar to shipping backends, payment backends must subclass 
shop.payment.payment_backends_base.BasePaymentBackend and be registerd in the
SHOP_PAYMENT_BACKENDS Django setting.

They also obtain a reference to the shop, with some convenient methods defined 
such as self.shop.get_order().

They must also define a get_urls() method, and all defined URLs will be 
namespaced to ``ship/``.
