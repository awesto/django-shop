.. reference/stock-management

================
Stock Management
================

Products in **django-SHOP**, by default do not keep track on their quantity in stock. This is
because the product model shall be as lean as possible, and properties shall only be added, if they
are required.

There are many shops which simply don't need to keep track their quantity in stock. Either because
the products they sell are arbitrarily reproducible, or because they share their stock with an
offline store and hence the availability is managed through other means, typically an ERP.

However, for concrete products, keeping track of their limited number of pieces in stock, is
mandatory. For this purpose **django-SHOP** offers two mutual exclusive product extensions. Without
configured stock management, products tagged as "available" are considered as available until
eternity and as unlimited in quantity.


Product with Quantity
=====================

A simple approach to keep track on the product's quantity in stock, is to store this information
side by side with the product model. This shall be done by adding a model field ``quantity``, using
an ``IntegerField``, ``PositiveIntegerField``, ``SmallIntegerField``, ``PositiveSmallIntegerField``,
``FloatField`` or a ``DecimalField``. The field type shall be the same as that used by the
``quantity``-field in :class:`shop.models.cart.CartItemModel`.

In addition to the field storing the quantity in stock, add the mixin class
:class:`shop.models.product.AvailableProductMixin` to the product model declaration. Example:

.. code-block:: python
	:caption: models.py

	from django.db import models
	from shop.models.product import BaseProduct, BaseProductManager, AvailableProductMixin

	class MyProduct(AvailableProductMixin, BaseProduct):
	    # other product fields

	    quantity = model.PositiveIntegerField(default=0)

	    class Meta:
	        app_label = app_settings.APP_LABEL

	    objects = BaseProductManager()

The latter mixin class overrides the two methods ``get_availability()`` and ``deduct_from_stock()``
taking into account that now the number of products in stock is limited.


Product with Inventory
======================

Sometimes it is not enough to just know the current number of items of a certain product. Consider
the use case, where a product is short in supply but the next incoming delivery is already
scheduled. In this situation a merchant might want to inform its customers, that the wanted product
isn't deliverable now but soon. Therefore, instead of adding a simple field storing the current
quantity, we add a relation for each delivered charge. This model then holds a timestamp, when the
next incoming delivery is expected. Example:

.. code-block:: python
	:caption: models.py

	from django.db import models
	from shop.models.product import BaseProduct, BaseProductManager
	from shop.models.inventory import BaseInventory, AvailableProductMixin

	class MyProduct(AvailableProductMixin, BaseProduct):
	    # product fields

	    class Meta:
	        app_label = app_settings.APP_LABEL

	    objects = BaseProductManager()

	class MyInventory(BaseInventory):
	    product = models.ForeignKey(
	        MyProduct,
	        related_name='inventory_set',
	    )

	    quantity = models.PositiveIntegerField(default=0)

Since we have a relation from the inventory to our product model, we must use an ``InlineModelAdmin``,
while creating our admin backend. Example:

.. code-block:: python
	:caption: admin.py

	from django.contrib import admin
	from myshop.models import MyProduct, Inventory

	class MyInventoryAdmin(admin.StackedInline):
	    model = MyInventory

	@admin.register(MyProduct)
	class MyProductAdmin(admin.ModelAdmin)
	    inlines = [MyInventoryAdmin]

This allows the merchant to schedule incoming deliveries.


Selling Short
-------------

If the timestamp for arrival is in between a short period of time, **django-SHOP** can *sell short*.
Selling short means to sell something which you actually don't own right now, but will own in the
future. The period of time for selling short, can be configured using the settings directive
``SHOP_SELL_SHORT_PERIOD``, using seconds or a Python ``timedelta`` object.


Time Limited Offer
------------------

An other possibility when using the Inventory relation, is to limit an offer for a determined
period of time. This is when the merchant sets the field named ``latest`` to a time stamp in the
near future. If this time stamp is in between the period configured using the settings directive
``SHOP_LIMITED_OFFER_PERIOD``, then the customer is notified that this offer is limited in time.


Reserving Products in Cart
==========================

Products keeping track of their quantity in stock, either with the simple approach, or with the
related inventory model have one behaviour in common – they deduct the number of items only during
the purchase operation. For short term product types, this behaviour is impractical, because of the
risk of overselling. Imagine a customer putting items into the cart and proceeding to checkout,
only to discover that these items are not available in the moment he wants to purchase his items.

Instead we want to reserve items, whenever a customer puts them into his cart. Then these items
are blocked for a certain period, normally only a few minutes, until they either have been puchased,
or a timeout occured, making them available for other customers again.

Independently of the chosen approach, replace ``AvailableProductMixin`` with ``ReserveProductMixin``
in the product's model declaration. Example for the simple approach:

.. code-block:: python
	:caption: models.py

	from shop.models.product import BaseProduct, ReserveProductMixin

	class MyProduct(ReserveProductMixin, BaseProduct):
	    # product fields

Example using the related inventory model. Here we use the class ``ReserveProductMixin`` from
the inventory module:

.. code-block:: python
	:caption: models.py

	from shop.models.product import BaseProduct
	from shop.models.inventory import ReserveProductMixin

	class MyProduct(ReserveProductMixin, BaseProduct):
	    # product fields

It is important to note, that when reserving products, it easily is possible to seemingly run short
of products, because customers just add them to their cart, without actually buying them. This may
result in a decrease of overall sales. Hence use this option only, if pending carts are flushed on a
regular basis.


Prevent Overselling
===================

in **django-SHOP**, purchasing the cart's content is performed as one transaction. This means
that either the cart is converted into an order as a whole, or left as it was before the customer
clicked the **Purchase Now**-button.

Now consider the following race-condition: Two customers add the same product to their carts. The
quantity of this product is limited in stock. As soon as one customer purchased this item, it is
not available anymore for the other customer. In such a situation the whole purchasing operation
is canceled for the second customer, so that he can look for an alternative product. If his
purchasing operation is canceled, an informative message is displayed, saying that the product
unexpectedly became unavailable.
