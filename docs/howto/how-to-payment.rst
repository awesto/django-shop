================================
How to create a Payment backend
================================

Payment backends must be listed in settings.SHOP_PAYMENT_BACKENDS

Shop interface
===============

While we could solve this with defining a superclass for all payment backends,
the better approach to plugins is to implement inversion-of-control, and let
the backends hold a reference to the shop instead.

The reference interface for payment backends is located at 
shop.payment.api.ShopPaymentAPI 

Currently, the shop interface defines the following methods:

Common with shipping
---------------------

* get_order(request): Returns the currently being processed order.
* add_extra_info(order, text): Adds an extra info filed to the order (whatever)
* is_order_payed(order): Whether the passed order is fully payed or not
* is_order_complete(order): Whether the passed order is in a "finished" state
* get_order_total(order): Returns the order's grand total.
* get_order_subtotal(order): Returns the order's sum of item prices (without 
  taxes or S&H)
* get_order_short_name(order): A short human-readable description of the order
* get_order_unique_id(order): The order's unique identifier for this shop system
* get_order_for_id(id): Returns an Order object given a unique identifier (this
  is the reverse of get_order_unique_id())

Specific to payment
--------------------
* confirm_payment(order, amount, transaction_id, save=True): This should be 
  called when the confirmation from the payment processor was called and that the
  payment was confirmed for a given amount. The processor's transaction 
  identifier should be passed too, along with an instruction to save the object 
  or not. For instance, if you expect many small confirmations you might want to 
  save all of them at the end in one go (?). Finally the payment method keeps track
  of what backend was used for this specific payment.

Backend interface
==================

The payment backend should define the following interface for the shop to be able
do to anything sensible with it:

Attributes
-----------

* backend_name : The name of the backend (to be displayed to users)
* url_namespace : "slug" to prepend to this backend's URLs (acting as a namespace)

Methods
--------

* __init__(): must accept a "shop" argument (to let the shop system inject a 
  reference to it)
* get_urls(): should return a list of URLs (similar to urlpatterns), to be added
  to the URL resolver when urls are loaded. Theses will be namespaced with the 
  url_namespace attribute by the shop system, so it shouldn't be done manually.
