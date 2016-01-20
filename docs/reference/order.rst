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

.. note:: Assure that the model ``OrderItem`` is imported (and materialized) before model
		``Product`` and classes derived from it.

Since the order item quantity can not always be represented by natural numbers, this field must be
added to the ``OrderItem`` implementation rather than its base class. Since quantities are copied
from the cart to the order, this field type must must correspond to ``CartItem.quantity``.

Whenever the customer performs the purchase operation, the cart object is converted into a new order
object by invoking:

.. code-block:: python

	from shop.models.order import OrderModel
	
	order = OrderModel.objects.create_from_cart(cart, request)

This operation is atomic and can take some time. It normally is performed by the payment provider,
whenever the payment was successfully received.

Since the merchants implementation of ``Cart``, ``CartItem``, ``Order`` and ``OrderItem`` may
contain extra fields the shop framework isn't aware of, these fields have to be converted from the
cart to the order objects during the purchasing operation.

If required the merchant's implementation of ``Order`` shall override the method
``populate_from_cart(cart, request)``, which provides a hook to copy those extra fields from the cart
object to the order object.

Similarly the merchant's implementation of ``OrderItem`` shall override the method
``populate_from_cart_item(cart_item, request)``, which provides a hook to copy those extra fields
from the cart item to the order item object.


Order Views
===========

Displaying the last or former orders in **djangoSHOP** is as simple, as adding two page to the CMS.
Change into the Django admin backend and enter into the CMS page tree. At an appropriate location
in that tree add a new page. As page title use "My Orders", "Ihre Bestellungen", "Mis Pedidos", or
whatever is appropriate in your language. Multilingual CMS installations offer a page title for each
language.

In the CMS page editor click onto the link named **Advanced Settings** at the bottom of the popup
window. As template, chose the default one, provided it contains at least one big placeholder_.

Enter "*shop-order*" into the **Id**-field just below. This identifier is required by some templates
which link directly onto the orders list view page. If this field is not set, some links onto this
page might not work properly.

The Order Views must be rendered by their own CMS apphook_. Locate the field **Application** and
chose "*View Orders*".

Below this "My Orders" page, add another page named "Thanks for Your Order", "Danke für Ihre
Bestellung" or "Gracias por su pedido". Change into the **Advanced Settings** view and as the
rendering template select "*Inherit the template of the nearest ancestor*". Next enter
"*shop-order-last*" into the **Id**-field just below. As **Application** chose again
"*View Orders*".


Add the Order list view via CMS-Cascade Plugin
----------------------------------------------

Click onto **View on site** and change into front-end editing mode to use the grid-system of
djangocms-cascade_. Locate the main placeholder and add a **Row** followed by at least one
**Column** plugin; both can be found in section **Bootstrap**. Below that column plugin, add a
child named **Order Views** from section **Shop**.

You have to perform this operation a second time for the page named "Thanks for Your Order". The
context menus for copying and pasting may be helpful here.

Note the the page "My Orders" handles two views: By invoking it as a normal CMS page, it renders
a list of all orders the currently logged in customer has purchased at this shop:

|order-list-view|

.. |order-list-view| image:: /_static/order/list-view.png

Clicking on one of the orders in this list, changes into a detail view, where one can see a list of
items purchased during that shopping session:

|order-detail-view| 

.. |order-detail-view| image:: /_static/order/detail-view.png

The rendered list is a historical snapshot of the cart in the moment of purchase. If in the meantime
the prices of products, tax rates, shipping costs or whatever changed, then that order object always
keeps the values at that time in history. This even applies to translations. Strings are translated
into their natural language on the moment of purchase. Therefore the labels added to the last rows
of the cart, always are rendered in the language which was used during the checkout process.


Render templates
~~~~~~~~~~~~~~~~

The path of the templates used to render the order views is constructed using the following rules:

* Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` in lower
  case. If no such folder can be found, then use the folder named ``shop``.
* Search for a subfolder named ``order``.
* Search for a template named ``list.html`` or ``detail.html``.

These templates are written to be easily extensible by the customized templates. To override them,
add a template with the path, say ``myshop/order/list.html`` to the projects template folder.


Order Workflows
===============

Order Workflows are simple plugins that allow the merchant to define rules in a programmatic way,
which actions to perform, whenever a certain event happened. A typical event is the confirmation
of a payment, which itself triggers further actions, say to print a delivery note.

Instead of implementing each possible combination for all of these use cases, the **djangoSHOP**
framework offers a `Finite State Machine`_, where only selected state transition can be marked as
possible. These transition further can trigger other events themselves. This prevents to perform
invalid actions such as fulfilling orders, which haven't been paid yet.




Cart Modifiers are split up into three different categories: Generic, Payment and Shipping. In the
shops ``settings.py`` they must be configured as a list or tuple such as:


.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html
.. _Finite State Machine: https://gist.github.com/Nagyman/9502133