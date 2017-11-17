=============================
Managing the Delivery Process
=============================

Depending on the merchant's setup, an order can be considered as one inseparably unit, or if partial
shipping shall be allowed, as a collection of single items, which can be delivered individually.

To enable partial shipping, assure the materialization of two classes inheriting from
:class:`shop.models.delivery.BaseDelivery` and :class:`shop.models.delivery.BaseDeliveryItem`. The
easiest way to do this is to import the default classes:

.. code-block:: python

	from shop.models.defaults.delivery import Delivery
	from shop.models.defaults.delivery_item import DeliveryItem

Typically, this is done in the project's ``admin.py`` file.

As with all models in **django-SHOP**, you can implement your own version of the delivery model.
This for instance is required, if the delivered quantity can not be expressed by an integer field.


Partial Delivery Workflow
=========================

The class implementing our ``Order`` model, requires additional methods provided by the mixin class
:class:`shop.shipping.delivery.PartialDeliveryWorkflowMixin`. Add this mixin class to the ordering
workflow by configuring:

.. code-block:: python

	SHOP_ORDER_WORKFLOWS = (
	    # other workflow mixins
	    'shop.shipping.workflows.PartialDeliveryWorkflowMixin',
	)

.. note:: Do not combine this mixin class with :class:`shop.shipping.workflows.CommissionGoodsWorkflowMixin`.


Administration Backend
======================

To control partial delivery, add the class :class:`shop.admin.delivery.DeliveryOrderAdminMixin`
to the class class implementing the ``OrderAdmin``:

.. code-block:: python
	:caption: myshop/admin/order.py

	from django.contrib import admin
	from shop.admin.defaults.order import OrderAdmin
	from shop.models.defaults.order import Order
	from shop.admin.delivery import DeliveryOrderAdminMixin

	@admin.register(Order)
	class OrderAdmin(DeliveryOrderAdminMixin, OrderAdmin):
	    pass


Implementation Details
======================

When partial delivery is activated, two additional tables are added to the database, one for each
delivery and one for each order item being delivered. This allows us to split up the quantity of in
ordered item into two or more delivery objects. This can be useful, if a product is sold out, but
the merchant wants to ship whatever is available on stock. He then creates a delivery object
and assigns the available quantity to each linked delivery item.

If a product is not available at all anymore, the merchant can alternatively cancel that order item.
