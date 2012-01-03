=======
Signals
=======

Order
=====

.. module:: shop.order_signals

The :mod:`shop.order_signals` module defines signals that are emitted during
the checkout process

.. warning::
    Currently, not all signals are emitted inside of django SHOP. This may
    change in the future.

``processing``
--------------

.. data:: shop.order_signals.processing
    :module:

Emitted when the :class:`~shop.models.Cart` instance was converted to an
:class:`~shop.models.Order`.

Arguments sent with this signal:

``sender``
    The :class:`~shop.models.Order` model class

``order``
    The :class:`~shop.models.Order` instance

``cart``
    The :class:`~shop.models.Cart` instance

``payment_selection``
---------------------

.. data:: shop.order_signals.payment_selection
    :module:

Emitted when the user is shown the "select a payment method" page.

Arguments sent with this signal:

``sender``
    The :class:`shop.shipping.api.ShippingAPI` instance

``order``
    The :class:`~shop.models.Order` instance

``confirmed``
-------------

.. data:: shop.order_signals.confirmed
    :module:

Emitted when the user finished placing his order (regardless of the payment
success or failure).

Arguments sent with this signal:

``sender``
    not defined

``order``
    The :class:`~shop.models.Order` instance

.. note::
    This signal is currently not emitted.

``completed``
-------------

.. data:: shop.order_signals.completed
    :module:

Emitted when the payment was received for the :class:`~shop.models.Order`. This
signal is emitted by the :class:`shop.views.checkout.ThankYouView`.

Arguments sent with this signal:

``sender``
    The :class:`~shop.views.checkout.ThankYouView` instance

``order``
    The :class:`~shop.models.Order` instance

``cancelled``
-------------

.. data:: shop.order_signals.cancelled
    :module:

Emitted if the payment was refused or other fatal problem.

Arguments sent with this signal:

``sender``
    not defined

``order``
    The :class:`~shop.models.Order` instance

.. note::
    This signal is currently not emitted.

``shipped``
-----------

.. data:: shop.order_signals.shipped
    :module:

Emitted (manually) when the shop clerk or robot shipped the order.

Arguments sent with this signal:

``sender``
    not defined

``order``
    The :class:`~shop.models.Order` instance

.. note::
    This signal is currently not emitted.