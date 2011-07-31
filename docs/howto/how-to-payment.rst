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

.. module:: shop.payment.api

.. class:: ShopPaymentAPI

Currently, the shop interface defines the following methods:

Common with shipping
---------------------

.. method:: ShopPaymentAPI.get_order(request)

    Returns the currently being processed order.
    
    :param request: a Django request object
    :rtype: a :class:`~shop.models.Order` instance

.. method:: ShopPaymentAPI.add_extra_info(order, text)

    Adds an extra info field to the order (whatever)

    :param order: an :class:`~shop.models.Order` instance
    :param text: a string containing the extra order information

.. method:: ShopPaymentAPI.is_order_payed(order)

    Whether the passed order is fully payed or not

    :param order: an :class:`~shop.models.Order` instance
    :rtype: :class:`bool`

.. method:: ShopPaymentAPI.is_order_complete(order)

    Whether the passed order is in a "finished" state

    :param order: an :class:`~shop.models.Order` instance
    :rtype: :class:`bool`

.. method:: ShopPaymentAPI.get_order_total(order)

    Returns the order's grand total.

    :param order: an :class:`~shop.models.Order` instance
    :rtype: :class:`~decimal.Decimal`

.. method:: ShopPaymentAPI.get_order_subtotal(order)

    Returns the order's sum of item prices (without taxes or S&H)

    :param order: an :class:`~shop.models.Order` instance
    :rtype: :class:`~decimal.Decimal`

.. method:: ShopPaymentAPI.get_order_short_name(order)

    A short human-readable description of the order

    :param order: an :class:`~shop.models.Order` instance
    :rtype: a string with the short name of the order

.. method:: ShopPaymentAPI.get_order_unique_id(order)

    The order's unique identifier for this shop system

    :param order: an :class:`~shop.models.Order` instance
    :rtype: the primary key of the :class:`~shop.models.Order` (in the default
        implementation)
    
.. method:: ShopPaymentAPI.get_order_for_id(id)

    Returns an :class:`~shop.models.Order` object given a unique identifier (this
    is the reverse of :meth:`get_order_unique_id`)

    :param id: identifier for the order
    :rtype: the :class:`~shop.models.Order` object identified by ``id``

Specific to payment
--------------------
.. method:: ShopPaymentAPI.confirm_payment(order, amount, transaction_id, save=True)

    This should be called when the confirmation from the payment processor was
    called and that the payment was confirmed for a given amount. The processor's
    transaction identifier should be passed too, along with an instruction to
    save the object or not. For instance, if you expect many small confirmations
    you might want to save all of them at the end in one go (?). Finally the
    payment method keeps track of what backend was used for this specific payment.

    :param order: an :class:`~shop.models.Order` instance
    :param amount: the payed amount
    :param transaction_id: the backend-specific transaction identifier
    :param save: a :class:`bool` that indicates if the changes should be committed
        to the database.

.. _payment-backend-interface:

Backend interface
==================

The payment backend should define the following interface for the shop to be able
do to anything sensible with it:

Attributes
-----------

.. attribute:: PaymentBackend.backend_name

    The name of the backend (to be displayed to users)

.. attribute:: PaymentBackend.url_namespace

    "slug" to prepend to this backend's URLs (acting as a namespace)

Methods
--------
.. method:: PaymentBackend.__init__(shop)

    must accept a "shop" argument (to let the shop system inject a
    reference to it)

    :param shop: an instance of the shop

.. method:: PaymentBackend.get_urls()

    should return a list of URLs (similar to urlpatterns), to be added
    to the URL resolver when urls are loaded. Theses will be namespaced with the
    url_namespace attribute by the shop system, so it shouldn't be done manually.

Security
---------

In order to make your payment backend compatible with the ``SHOP_FORCE_LOGIN``
setting please make sure to add the ``@shop_login_required`` decorator to any
views that your backend provides. See :ref:`how-to-secure-your-views` for more
information.
