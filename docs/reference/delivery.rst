.. _reference/delivery:

============================
Managing the Deliver Process
============================

Depending on the merchant's setup, an order can be considered as one inseparably unit, or if partial
shipping shall be allowed, as a collection of single products, which can be delivered individually.

To enable partial shipping, assure the instantiation of both classes
:class:`shop.models.delivery.BaseDelivery` and :class:`shop.models.delivery.BaseDeliveryItem`. The
easiest way to do this is to import the materialized classes into an existing model class:

.. code-block:: python

	from shop.models.defaults.delivery import Delivery, DeliveryItem


Partial Delivery Workflow
=========================

The class implementing the ``Order``, requires additional methods provided by the mixin class
:class:`shop.shipping.delivery.PartialDeliveryWorkflowMixin`. Mix this class into the ``Order``
class by configuring

.. code-block:: python

	SHOP_ORDER_WORKFLOWS = (
	    # other workflow mixins
	    'shop.shipping.defaults.PartialDeliveryWorkflowMixin',
	)

.. note:: Do not combine this mixin with the class ``CommissionGoodsWorkflowMixin``.


Administration Backend
======================

To control partial delivery, add the class :class:`shop.admin.delivery.DeliveryOrderAdminMixin`
to the amin class class implementing an ``Order``:

.. code-block:: python
	:caption: myshop/admin/order.py

	from django.contrib import admin
	from shop.admin.order import BaseOrderAdmin
	from shop.models.defaults.order import Order
	from shop.admin.delivery import DeliveryOrderAdminMixin

	@admin.register(Order)
	class OrderAdmin(DeliveryOrderAdminMixin, BaseOrderAdmin):
	    pass


Implementation Details
======================

When partial delivery is activated, two additional tables are added to the database, one for each
delivery and one for each delivered order item. This allows us to split up the quantity of in
ordered item into two or more delivery objects. This can be useful, if a product is sold out, but
the merchant wants to ship whatever is available on stock. He then creates a delivery object
and assigns the available quantity to each linked delivery item.

If a product is not available at all anymore, the merchant can alternatively cancel that order item.
