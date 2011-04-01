================================
How to create a Payment backend
================================

* Payment backends must subclass shop.paymemt.payment_backend_base.BasePaymentBackend
* Payment backends must be listed in settings.SHOP_PAYMENT_BACKENDS

Shop interface
===============

While we could solve this with defining a superclass for all payment backends,
the better approach to plugins is to implement inversion-of-control, and let
the backends hold a reference to the shop instead.

The reference interface for payment backends is located at 
shop.payment.payment_backend_base.PaymentBackendAPI 


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
