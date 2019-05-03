.. _reference/order:

=====
Order
=====

During checkout, at a certain point the customer has to click on a button named "*Purchase Now*".
This operation performs quite a few tasks: One of them is to convert the cart with its items into
an order. The final task is to reset the cart, which means to remove its content. This operation
is atomic and not reversible.


Order Models
============

An order consists of two models classes ``Order`` and ``OrderItem``, both inheriting from
``BaseOrder`` and ``BaseOrderItem`` respectively. As with most models in **django-SHOP**, they are
:ref:`reference/deferred-models`, so that inheriting from a base class automatically sets the
foreign keys to the appropriate model. This gives the programmer the flexibility to add as many
fields to the order model, as the merchant requires for his special implementation.

In most use-cases, the default implementation of the order model will do the job. These default
classes can be found at :class:`shop.models.defaults.order.Order` and
:class:`shop.models.defaults.order_item.OrderItem`. To materialize the default implementation, it
is enough to ``import`` these two files into the merchant's shop project. Otherwise the programmer
may create his own order implementation inheriting from ``BaseOrder`` and/or ``BaseOrderItem``.

.. note:: Assure that the model ``OrderItem`` is imported (and materialized) before model
		``Product`` and classes derived from it.

The order item quantity can not always be represented by natural numbers, therefore this field must
be added to the ``OrderItem`` implementation rather than its base class. Since the quantity is
copied from the cart item to the order item, its field type must must correspond to that of
``CartItem.quantity``.


Create an Order from the Cart
-----------------------------

Whenever the customer performs the purchase operation, the cart object is converted into a new order
object by invoking:

.. code-block:: python

	from shop.models.order import OrderModel

	order = OrderModel.objects.create_from_cart(cart, request)
	order.populate_from_cart(cart, request)

This invocation of ``order.populate_from_cart`` operation is atomic and can take some time. It
normally is performed by the payment provider, whenever a successful payment was received.

Since the merchant's implementation of ``Cart``, ``CartItem``, ``Order`` and ``OrderItem`` may
contain extra fields the shop framework isn't aware of, the content of these fields also shall be
transferred, whenever a cart is converted into an order object, during the purchasing operation.

If required, the merchant's implementation of ``Order`` shall override the method
``populate_from_cart(cart, request)``, which provides a hook to copy those extra fields from the
cart object to the order object.

Similarly the merchant's implementation of ``OrderItem`` shall override the method
``populate_from_cart_item(cart_item, request)``, which provides a hook to copy those extra fields
from the cart item to the order item object.


Order Numbers
-------------

In commerce it is mandatory that orders are numbered using a unique and continuously increasing
sequence. Each merchant has his own way to generate this sequence numbers and in some
implementations it may even come from an external generator, such as an ERP system. Therefore
**django-SHOP** does not impose any numbering scheme for the orders. This intentionally is left
over to the merchant's implementation, which may be implemented as:

.. code-block:: python

	from django.db import models
	from django.utils.datetime_safe import datetime
	from shop.models import order

	class Order(order.BaseOrder):
	    number = models.PositiveIntegerField("Order Number", null=True, default=None, unique=True)

	    def get_or_assign_number(self):
	        if self.number is None:
	            epoch = datetime.now().date()
	            epoch = epoch.replace(epoch.year, 1, 1)
	            qs = Order.objects.filter(number__isnull=False, created_at__gt=epoch)
	            qs = qs.aggregate(models.Max('number'))
	            try:
	                epoc_number = int(str(qs['number__max'])[4:]) + 1
	                self.number = int('{0}{1:05d}'.format(epoch.year, epoc_number))
	            except (KeyError, ValueError):
	                # the first order this year
	                self.number = int('{0}00001'.format(epoch.year))
	        return self.get_number()

	    def get_number(self):
	        return '{0}-{1}'.format(str(self.number)[:4], str(self.number)[4:])

	    @classmethod
	    def resolve_number(cls, number):
	        number = number[:4] + number[5:]
	        return dict(number=number)


Here we override these three methods, otherwise the order number would be identical to its primary
key which is not suitable for all e-commerce sites.


Method ``get_or_assign_number()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Is used to assign a new number to an Order object, if none has been assigned yet, otherwise it
returns the assigned one.


Method ``get_number()``
~~~~~~~~~~~~~~~~~~~~~~~

Retrieves the order number assigned to an order in a human readable form. Here the first four
digits specify the year in which the order was generated, whereas the last five digits are a
continuous increasing sequence.



Classmethod ``resolve_number(number)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Chances are high that we use the order number as slug, or for any other similar identification
purpose. If we look up for a certain order object using ``Order.objects.get(...)`` or
``Order.objects.filter(...)``, then we might want to use a number previously retrieved with
``get_number``. This classmethod therefore must reverse the operation of building order numbers.


Order Views
===========

Displaying the last or former orders in **django-SHOP** is as simple, as adding two pages to the
CMS. Change into the Django admin backend and enter into the CMS page tree. At an appropriate
location in that tree add a new page. As page title use "My Orders", "Ihre Bestellungen",
"Mis Pedidos", or whatever is appropriate in the natural language used for that site.
Multilingual CMS installations offer a page title for each language.

In the CMS page editor click onto the link named **Advanced Settings** at the bottom of the popup
window. As template, choose the default one, provided it contains at least one big placeholder_.

Enter "*shop-order*" into the **Id**-field just below. This identifier is required by some templates
which link directly onto the orders list view page. If this field is not set, some links onto this
page might not work properly.

The Order Views must be rendered by their own CMS apphook_. Locate the field **Application** and
choose "*View Orders*".

Below this "My Orders" page, add another page named "Thanks for Your Order", "Danke für Ihre
Bestellung" or "Gracias por su pedido". Change into the **Advanced Settings** view and as the
rendering template select "*Inherit the template of the nearest ancestor*". Next enter
"*shop-order-last*" into the **Id**-field just below. As **Application** choose again
"*View Orders*".


CMS Apphook for the Order
-------------------------

The apphook for the Order View must be provided by the Django project. This is a simple snippet of
boilerplate which has to be added to the merchant's implementation of the file
``myshop/cms_apps.py``:

.. code-block:: python

	from cms.apphook_pool import apphook_pool
	from shop.cms_apphooks import OrderCMSApp

	class OrderApp(OrderCMSApp):
	    pass

	apphook_pool.register(OrderApp)


This apphook uses the class :class:`shop.views.order.OrderView` to render the order's list- and
detail views using the serializers :class:`shop.serializers.order.OrderListSerializer` and
:class:`shop.serializers.order.OrderDetailSerializer`. Sometimes these defaults aren't enough and
must be extended by a customized serializer. Say, our Order class contains the rendered
shipping and billing addresses. Then we can extend our serializer class by adding them:

.. code-block:: python
	:caption: myshop/serializers.py

	from shop.serializers.order import OrderDetailSerializer

	class CustomOrderSerializer(OrderDetailSerializer):
	    shipping_address_text = serializers.CharField(read_only=True)
	    billing_address_text = serializers.CharField(read_only=True)

We now can replace the ``urls`` attribute in our apphook class with, say ``['myshop.urls.order']``
and exchange the default serializer with our customized one:

.. code-block:: python
	:caption: myshop/urls/order.py

	from django.conf.urls import url
	from shop.views.order import OrderView
	from myshop.serializers import CustomOrderSerializer

	urlpatterns = [
	    url(r'^$', OrderView.as_view()),
	    url(r'^(?P<pk>\d+)$', OrderView.as_view(many=False,
	        detail_serializer_class=CustomOrderSerializer)),
	]

Now, when invoking the order detail page appending ``?format=api`` to the URL, then two new fields,
``shipping_address_text`` and ``billing_address_text`` shall appear in our context.


Add the Order list view via CMS-Cascade Plugin
----------------------------------------------

Click onto **View on site** and change into front-end editing mode to use the grid-system of
djangocms-cascade_. Locate the main placeholder and add a **Row** followed by at least one
**Column** plugin; both can be found in section **Bootstrap**. Below that column plugin, add a
child named **Order Views** from section **Shop**.

We have to perform this operation a second time for the page named "Thanks for Your Order". The
context menus for copying and pasting may be helpful here.

Note that the page "My Orders" handles two views: By invoking it as a normal CMS page, it renders
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


.. _reference/order-workflows:

Order Workflows
===============

Order Workflows are simple plugins that allow the merchant to define rules in a programmatic way,
which actions to perform, whenever a certain event happened. A typical event is the confirmation
of a payment, which itself triggers further actions, say to print a delivery note.

Instead of implementing each possible combination for all of these use cases, the **django-SHOP**
framework offers a `Finite State Machine`_, where only selected state transition can be marked as
possible. These transition further can trigger other events themselves. This prevents to accidently
perform invalid actions such as fulfilling orders, which haven't been paid yet.

In class :class:`shop.models.order.BaseOrder` contains an attribute ``status`` which is of type
``FSMField``. In practice this is a char-field, which can hold preconfigured states, but which
*can not* be changed by program code. Instead, by calling specially decorated class methods, this
state then changes from one or more allowed source states into one predefined target state. We
denote this as a *state transition*.

An incomplete example:

.. code-block:: python

	class Order(models.Model):
	    # other attributes

	    @transition(field=status, source='new', target='created')
	    def populate_from_cart(self, cart, request):
	        # perform some side effects ...

Whenever an ``Order`` object is initialized, its ``status`` is *new* and is not yet populated
with cart items, meaning that it resides in a pending state. As we have seen earlier, this object
must be populated from the cart. If this succeeds, the ``status`` of our new ``Order`` object
switches to *created*.

In **django-SHOP** the merchant can add as many payment providers he wants. This is done in
``settings.py`` through the configuration directive ``SHOP_ORDER_WORKFLOWS`` which takes a list of
so called "*Order Workflow Mixin*" classes. On bootstrapping the application and constructing the
``Order`` class, it additionally inherits from these mixin classes. This gives the merchant an easy
to configure, yet very powerful tool to model the selling process of his e-commerce site according
to his needs. Say, we want to accept bank transfer in advance, so we must add
``'shop.payment.defaults.PayInAdvanceWorkflowMixin'`` to our configuration setting. Additionally we
must assure that the checkout process has been configured to offer the corresponding cart modifier:

.. code-block:: python

	SHOP_CART_MODIFIERS = (
	    ...
	    'shop.modifiers.defaults.PayInAdvanceModifier',
	    ...
	)

This mixin class contains a few transition methods, lets for instance have a closer look onto

.. code-block:: python

	    @transition(field='status', source=['created'], target='awaiting_payment')
	    def awaiting_payment(self):
	         """Signals that an Order awaits payments."""

This method actually does nothing, beside changing the status from "*created*" to
"*awaiting_payment*". It is invoked by the method ``get_payment_request()`` from
``ForwardFundPayment``, which is the default payment provider of the configured
``PayInAdvanceModifier`` cart modifier.

The class ``PayInAdvanceWorkflowMixin`` has two other transition methods worth mentioning:

.. code-block:: python

	    @transition(field='status', source=['awaiting_payment'],
	        target='prepayment_deposited', conditions=[is_fully_paid],
	        custom=dict(admin=True, button_name=_("Mark as Paid")))
	    def prepayment_fully_deposited(self):
	        """Signals that the current Order received a payment."""

This method can be invoked by the Django admin backend when saving an existing Order object, but
only under the condition that it is fully paid. The method ``is_fully_paid()`` iterates over all
payments associated with its Order object, sums them up and compares them against the total. If the
entered payment equals or exceeds the order's total, this method returns ``True`` and the condition
for the given transition is met. This then adds a button labeled "*Mark as Paid*" at the bottom of
the admin view. Whenever the merchant clicks on this button, the above method
``prepayment_fully_deposited`` is invoked. This then changes the order's status from
"*awaiting_payment*" to "*prepayment_deposited*". The :ref:`reference/notifications` of
**django-SHOP** can intercept this transition change and perform preconfigured action, such as
sending a payment confirmation email to the customer.

Now that the order has been paid, it time to fulfill it. For this a merchant can use the workflow
mixin class :class:`shop.shipping.defaults.CommissionGoodsWorkflowMixin`, which gives him a
hand to keep track on the fulfillment of each order. Since this class doesn't know anything
about an order status of "*prepayment_deposited*" (this is a private definition of the class
``PayInAdvanceWorkflowMixin``), **django-SHOP** provides a status to mark the payment of an order as
confirmed. Therefore another transition is added to our mixin class, which is invoked automatically
by the framework whenever the status changes to "*prepayment_deposited*":

.. code-block:: python

	@transition(field='status', source=['prepayment_deposited',
	    'no_payment_required'], custom=dict(auto=True))
	def acknowledge_prepayment(self):
	    """Acknowledge the payment."""
	    self.acknowledge_payment()

This status, "*payment_confirmed*", is known by all other workflow mixin classes and must be used
as the source argument for their transition methods.

For further details on Finite State Machine transitions, please refer to the `FSM docs`_. This
however does not cover the contents of dictionary ``custom``. One of the attributes in ``custom``
is ``button="Any Label"`` as explained in the `FSM admin docs`_. The other is ``auto=True``
and has been introduced by **django-SHOP** itself. It is used to automatically proceed from
one target to another one, without manual intervention, such as clicking onto a button.


Signals
-------

Each state transition emits a signal_ before and after performing the status change. These signals,
``pre_transition`` and ``post_transition`` can be received by any registered signal handler. In
**django-SHOP**, the notification framework listens for these events and creates appropriate
notification e-mails, if configured.

But sometimes simple notifications are not enough, and the merchant's implementation must perform
actions in a programmatic way. This for instance could be a query, which shall be sent to the goods
management database, whenever a payment has been confirmed successfully.

In Django, we typically register signal handlers in the ``ready`` method of the merchant's
`application configuration`_:

.. code-block:: python
	:caption: myshop/apps.py

	from django.apps import AppConfig

	class MyShopConfig(AppConfig):
	    name = 'my_shop'

	    def ready(self):
	        from django_fsm.signals import post_transition
	        post_transition.connect(order_event_notification)

	def order_event_notification(sender, instance=None, target=None, **kwargs):
	    if target == 'payment_confirmed':
	        # do whatever appropriate

In the above order event notification, use ``instance`` to access the corresponding ``Order``
object.


Finite State Machine Diagram
----------------------------

If graphviz_ is installed on the operating system, it is pretty simple to render a graphical
representation of the currently configured Finite State Machine. Simply invoke:

.. code-block:: shell

	./manage.py ./manage.py graph_transitions -o fsm-graph.png

Applied to our demo shop, this gives the following graph:

|fsm-graph|

.. |fsm-graph| image:: /_static/order/fsm-graph.png


Order Admin
===========

The order admin backend is likely the most heavily used editor for **django-SHOP** installation.
Here the merchant must manage all incoming orders, payments, customer annotations, deliveries, etc.
By automating common tasks, the backend shall prevent careless mistakes: It should for instance
neither be possible to ship unpaid goods, nor to cancel a delivered order.

Since the **django-SHOP** framework does not know which class model is used to implement an
``Order``, it intentionally doesn't register its prepared administration class for that model.
This has to be done by the merchant implementing the shop. It allows to add additional fields and
other mixin classes, before registration.

For instance, the admin class used to manage the ``Order`` model in our shop project, could be
implemented as:

.. code-block:: python
	:caption: myshop/admin.py

	from django.contrib import admin
	from shop.models.order import OrderModel
	from shop.admin.order import (PrintInvoiceAdminMixin,
	    BaseOrderAdmin, OrderPaymentInline, OrderItemInline)

	@admin.register(OrderModel)
	class OrderAdmin(PrintInvoiceAdminMixin, BaseOrderAdmin):
	    fields = BaseOrderAdmin.fields + (
	        ('shipping_address_text', 'billing_address_text',),)
	    inlines = (OrderItemInline, OrderPaymentInline,)

The fields ``shipping_address_text`` and ``billing_address_text`` are not part of the abstract model
class ``BaseOrder`` and therefore must be referenced separately.

Another useful mixin class to be added to this admin backend is ``PrintInvoiceAdminMixin``. Whenever
the status of an order shows it has been paid, a button labeled "*Print Invoice*" is added to the
order admin form. Clicking on that button displays one ore more pages optimized for printing.

The template for the invoice and delivery note can easily be adopted to the corporate design using
plain HTML and CSS.


Rendering extra fields
----------------------

The models ``Order`` and ``OrderItems`` both contain a JSON fiels to hold arbitary data, collected
during the checkout process. Here for instance, **django-SHOP** stores the computations as performed
by the :ref:`reference/cart-modifiers`. Displaying them in Django's admin backend would result in
a rendered Python dictionary, which is not well readable by humans.

Therefore the merchant may add a template, which is rendered using the content of that JSON field,
named ``extra``. For the implemented order model the merchant may add a template named
``<myshop>/admin/order-extra.html`` to its template folder. This template then shall render all the
fields as available inside that JSON field. Here ``rows`` contains a list of computations added
by the cart modifiers.

Additionally, a merchant may add templates which are rendered using the contents of the JSON fields,
for each of the order item associated with the given order. Since order items can refer to different
types of products, we may add a template for each of them. It is named
``<myshop>/admin/orderitem-<productname>-extra.html`` whereas *productname* is the class name in
lowercase of the model implementing that product. If no such template could be found, then a
template named ``<myshop>/admin/orderitem-product-extra.html`` is used as fallback. If no template
is provided, then the content of these extra fields is not rendered.


Re-adding an Order to the Cart
==============================

Sometimes it can be useful to re-add the content of an order back to the cart. This functionality
currently is implemented only via the REST-API. By checking the field ``reorder`` before posting
the data, the content of the given order is copyied into the cart.


.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html
.. _djangocms-cascade: http://djangocms-cascade.readthedocs.org/en/latest/
.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders
.. _Finite State Machine: https://gist.github.com/Nagyman/9502133
.. _graphviz: http://www.graphviz.org/
.. _FSM docs: https://github.com/kmmbvnr/django-fsm
.. _FSM admin docs: https://github.com/gadventures/django-fsm-admin
.. _signal: https://docs.djangoproject.com/en/stable/topics/signals/
.. _application configuration: https://docs.djangoproject.com/en/1.9/ref/applications/#application-configuration
