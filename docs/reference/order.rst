.. _order:

=========
The Order
=========

During checkout, at a certain point, the customer has to click on a button name "Purchase Now".
This operation performs quite a few tasks, one of them is to convert the cart with its items into
an order. The final task is to reset the cart, which means to remove its content. This operation
is atomic and not reversible.


Order Models
============

An order consists of two models classes ``Order`` and ``OrderItem``, both inheriting from
``BaseOrder`` and ``BaseOrderItem`` respectively. As with most models in **djangoSHOP**, these are
:ref:`deferred-models`, so that inheriting from a base class automatically sets the foreign keys to
the appropriate model. This gives the programmer the flexibility to add as many fields to the order,
as the merchant requires for his special implementation.

In most use-cases, the default order implementation will do the job. These default classes can be
found at :class:`shop.models.defaults.order.Order` and
:class:`shop.models.defaults.order_item.OrderItem`. To materialize the default implementation, it
is enough to ``import`` these two files into the merchants shop project. Otherwise the programmer
may create his own order implementation inheriting from ``BaseOrder`` and/or ``BaseOrderItem``.

Since the order item quantity can not always be represented by natural numbers, this field must be
added to the ``OrderItem`` implementation rather than its base class. Since quantities are copied
from the cart to the order, this field type must must correspond to ``CartItem.quantity``.

Whenever the customer performs a purchase operation, the cart is converted into an order. Since
the merchants implementation of ``Order`` and ``OrderItem`` may contain some extra fields, 

, use the method 


The ``Order`` model contains 



In case some extra arbitrary information has to be added to the cart or its items, add
``extras = JSONField()`` to the ``Cart`` and/or ``CartItem`` models. This allows the merchant to
keep track on product variations and other random stuff.

