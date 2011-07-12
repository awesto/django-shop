==================================
How to create a shipping backend 
==================================

* Shipping backends must be listed in settings.SHOP_SHIPPING_BACKENDS

Shop interface
===============

While we could solve this with defining a superclass for all shipping backends,
the better approach to plugins is to implement inversion-of-control, and let
the backends hold a reference to the shop instead.

The reference interface for shipping backends is located at 
shop.shipping.shipping_backend_base.ShippingBackendAPI 

.. _shipping-backend-interface:

Backend interface
==================

The shipping backend should define the following interface for the shop to be able
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

Security
---------

In order to make your shipping backend compatible with the ``SHOP_FORCE_LOGIN``
setting please make sure to add the ``@shop_login_required`` decorator to any
views that your backend provides. See ``how-to-secure-your-views.rts`` for more
information.
