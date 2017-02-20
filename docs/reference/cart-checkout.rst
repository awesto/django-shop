.. _reference/cart-checkout:

=================
Cart and Checkout
=================

In **django-SHOP** the cart's content is always stored inside the database. In previous versions of
the software, the cart's content was kept inside the session for anonymous users and stored in the
database for logged in users. Now the cart is always stored in the database. This approach
simplifies the code and saves some random access memory, but adds another minor problem:

From a technical point of view, the checkout page is the same as the cart. They can both be on
separate pages, or be merged on the same page. Since what we would normally name the
"*Checkout Page*", is only a collection of :ref:`reference/cascade-plugins`, we won't go into
further detail here.


Expired Carts
=============

Sessions expire, but then the cart's content of anonymous customers still remains in the database.
We therefore must assure that these carts will expire too, since they are of no use for anybody,
except, maybe for some data-mining experts.

By invoking

.. code-block:: shell

	./manage.py shopcustomers
	Customers in this shop: total=3408, anonymous=140, expired=88,
	    active=1108, guests=2159, registered=1109, staff=5.

we gather some statistics about customers having visited of our **django-SHOP** site. In this example
we see that 1109 customers bought as registered users, while 2159 bought as guests. There are 88
customers in the database, but they don't have any associated session anymore, hence they can be
considered as expired. Invoking

.. code-block:: shell

	./manage.py shopcustomers --delete-expired

deletes those expired customers, and with them their expired carts. This task shall be performed
by a cronjob on a daily or weekly basis.


Cart Models
===========

The cart consists of two models classes ``Cart`` and ``CartItem``, both inheriting from ``BaseCart``
and ``BaseCartItem`` respectively. As with most models in **django-SHOP**, these are using the
:ref:`reference/deferred-models`, so that inheriting from a base class automatically sets the
foreign keys to the appropriate model. This gives the programmer the flexibility to add as many
fields to the cart, as the merchant requires for his special implementation.

In most use-cases, the default cart implementation will do the job. These default classes can be
found at :class:`shop.models.defaults.cart.Cart` and :class:`shop.models.defaults.cart_item.CartItem`.
To materialize the default implementation, it is enough to ``import`` these two files into the
merchants shop project. Otherwise we create our own cart implementation inheriting from ``BaseCart``
and ``BaseCartItem``. Since the item quantity can not always be represented by natural numbers, this
field must be added to the ``CartItem`` implementation rather than its base class. Its field type
must allow arithmetic operations, so only ``IntegerField``, ``FloatField`` or ``DecimalField``
are allowed as quantity.

.. note:: Assure that the model ``CartItem`` is imported (and materialized) before model
		``Product`` and classes derived from it.

The ``Cart`` model uses its own manager. Since there is only one cart per customer, accessing the
cart must be performed using the ``request`` object. We can always access the cart for the current
customer by invoking:

.. code-block:: python

	from shop.models.cart import CartManager

	cart = CartModel.objects.get_or_create_from_request(request)

Adding a product to the cart, must be performed by invoking:

.. code-block:: python

	from shop.models.cart import CartItemManager

	cart_item = CartItemManager.get_or_create(
	    cart=cart, product=product, quantity=quantity, **extras)

This returns a new cart item object, if the given product could not be found in the current cart.
Otherwise it returns the existing cart item, increasing the quantity by the given value. For
products with variations it's not always trivial to determine if they shall be considered as
existing cart items, or as new ones. Since **django-SHOP** can't tell that difference for any kind
of product, it delegates this question. Therefore the class implementing the shop's products shall
override their method ``is_in_cart``. This method is used to tell the ``CartItemManager`` whether a
product has already been added to the cart or is new.

Whenever the method ``cart.update(request)`` is invoked, the cart modifiers run against all items
in the cart. This updates the line totals, the subtotal, extra costs and the final sum.


Watch List
----------

Instead of implementing a separate watch-list (some would say wish-list), **django-SHOP** uses a
simple trick. Whenever the quantity of a cart item is zero, this item is considered to be in the
watch list. Otherwise it is considered to be in the cart. The train of though is as follows:
A quantity of zero, never makes sense for items in the cart. On the other side, any quantity
makes sense for items in the watch-list. Therefore reducing the quantity of a cart item to zero is
the same as keeping an eye on it, without actually wanting it to purchase.


Cart Views
==========

Displaying the cart in **django-SHOP** is as simple, as adding any other page to the CMS. Change into
the Django admin backend and enter into the CMS page tree. At an appropriate location in that tree
add a new page. As page title use "Cart", "Basket", "Warenkorb", "Cesta", or whatever is appropriate
in the natural language used for that site. Multilingual CMS installations offer a page title for
each language.

In the CMS page editor click onto the link named **Advanced Settings** at the bottom of the popup
window. As template, choose the default one, provided it contains at least one big placeholder_.

Enter "shop-cart" into the **Id**-field just below. This identifier is required by some templates
which link directly onto the cart view page. If this field is not set, some links onto the cart page
might not work properly.

It is suggested to check the checkbox named **Soft root**. This prevents that a menu item named
"Cart" will appear side by side with other pages from the CMS. Instead, we prefer to render a
special cart symbol located on the right of the navigation bar.


.. _reference/cart-cascade-plugin:

Cart using a Cascade Plugin
---------------------------

Click onto **View on site** and change into front-end editing mode to use the grid-system of
djangocms-cascade_. Locate the main placeholder and add a **Row** followed by at least one
**Column** plugin; both can be found in section **Bootstrap**. Below that column plugin, add a
child named **Cart** from section **Shop**. This Cart Plugin can be rendered in four different
ways:

|cart-structure|

.. |cart-structure| image:: /_static/cart/cart-structure.png


Editable Cart
~~~~~~~~~~~~~

An "Editable Cart" is rendered using the Angular JS template engine. This means that a customer
may change the number of items, delete them or move them to the watch-list. Each update is reflected
immediately into the cart's subtotal, extra fields and final totals.

Using the above structure, the rendered cart will look similar to this.

|cart-display|

.. |cart-display| image:: /_static/cart/cart-display.png

Depending on the chosen template, this layout may vary.


Static Cart
~~~~~~~~~~~~

An alternative to the editable cart is the *static cart*. Here the cart items are rendered by
the Django template engine. Since here everything is static, the quantity can't be changed anymore
and the customer would have to proceed to the checkout without being able to change his mind. This
probably only makes sense when purchasing a single product.


Cart Summary
~~~~~~~~~~~~

This only displays the cart's subtotal, the extra cart fields, such as V.A.T., shipping costs and
the final total.


Watch List
~~~~~~~~~~

A special view of the cart is the watch list. It can be used by customers to remember items they
want to compare or buy sometimes later. The watch-list by default is editable, but does not
allow to change the quantity. This is because the watch-list shares the same object model as the
cart items. If the quantity of an item 0, then that cart item is considered to be watched. If
instead the quantity is 1 ore more, the item is considered to be in the cart. It therefore is
very easy to move items from the cart to the watch-list and vice versa. This concept also disallows
to have an item in both the cart and the watch-list. This during online shopping, often can be a
major point of confusion.


.. _reference/cart-render-templates:

Render templates
~~~~~~~~~~~~~~~~

The path of the templates used to render the cart views is constructed using the following rules:

* Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` in lower
  case. If no such folder can be found, then use the folder named ``shop``.
* Search for a subfolder named ``cart``.
* Search for a template named ``editable.html``, ``static.html``, ``watch.html`` or ``summary.html``.

These templates are written to be easily extensible by the customized templates. To override the
"*editable cart*" add a template with the path, say ``myshop/cart/editable.html`` to the projects
template folder. This template then shall begin with ``{% extend "shop/cart/editable.html" %}``
and only override the ``{% block %}...{% endblock %}`` interested in.

Many of these template blocks are themselves embedded inside HTML elements such as
``<script id="shop/....html" type="text/ng-template">``. The reason for this is that the editable
cart is rendered in the browser by AngularJS using so called `directives`_. Hence it becomes very
straight-forward to override Angular's `script templates`_ using Django's internal template engine.


Multiple templates
..................

If for some special reasons we need different cart templates, then we must add this line to the
projects ``settings.py``:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES = {
	    'ShopCartPlugin': (
	        (None, _("default")),  # the default behavior
	        ('myproject/cart/other-editable.html', _("extra editable")),
	    )
	}

This will add an extra select button to the cart editor. The site administrator then can choose
between the default template and an extra editable cart template.


Proceed to Checkout
...................

On the cart's view, the merchant may decide whether to implement the checkout forms together with
the cart, or to create a special checkout page onto which the customer can proceed. From a technical
point of view, it doesn't make any difference, if the cart and the checkout are combined on the same
CMS page, or if they are split across two or more pages. In the latter case simply add a button at
the end of each page, so that the customer can easily proceed to the next one.

On the checkout page, the customer has to fill out a few forms. These can be a contact form,
shipping and billing addresses, payment and shipping methods, and many more. Which ones depend on
the configuration, the legal regulations and the requirements of the shop's implementation. In
:ref:`reference/cascade-plugins` all shop specific CMS plugins are listed. They can be combined
into whatever makes sense for a successful checkout.


Add a Cart via manually written Cart Template
---------------------------------------------

Instead of using the CMS plugin system, the template for the cart can also be implemented manually.
Based on an existing page template, locate the element, where the cart shall be inserted. Then
use one of the existing templates in the folder ``django-shop/shop/templates/shop/cart/`` as a
starting point, and insert it at an appropriate location in the page template. Next, in the
project's ``settings.py``, add this specialized template to the list ``CMS_TEMPLATES`` and select
it for that page.

From a technical point of view, it does not make any difference whether we use the cart plugin or a
handcrafted template. If the HTML code making up the cart has to be adopted to the merchants needs,
we normally are better off and much more flexible, if we override the template code as described
in section :ref:`reference/cart-render-templates`. Therefore, it is strongly discouraged to craft
cart and checkout templates by hand.


.. _reference/cart-modifiers:

Cart Modifiers
==============

Cart Modifiers are simple plugins that allow the merchant to define rules in a programmatic way,
how the totals of a cart are computed and how they are labeled. A typical job is to compute tax
rates, adding discounts, shipping and payment costs, etc.

Instead of implementing each possible combination for all of these use cases, the **django-SHOP**
framework offers an API, where third party applications can hooks into every computational step.
One thing to note here is that Cart Modifiers are not only invoked, when the cart is complete and
the customer wants to proceed to the checkout, but also for each item before being added to the
cart.

This allows the programmer to vary the price of certain items, depending on the current state of
the cart. It can for instance be used, to set one price for the first item, and other prices for
every further items added to the cart.

Cart Modifiers are split up into three different categories: Generic, Payment and Shipping. In the
shops ``settings.py`` they must be configured as a list or tuple such as:

.. code-block:: python

	SHOP_CART_MODIFIERS = (
	    'shop.modifiers.defaults.DefaultCartModifier',
	    'shop.modifiers.taxes.CartExcludedTaxModifier',
	    'myshop.modifiers.PostalShippingModifier',
	    'shop.modifiers.defaults.PayInAdvanceModifier',
	    'shop_stripe.modifiers.StripePaymentModifier',
	)

Generic modifiers are applied always. The Shipping and Payment modifiers are applied only for the
selected shipping and/or payment method. If the customer has not yet decided, how to ship or how to
pay, then the corresponding modifiers are not applied.

When updating the cart, modifiers are applied in the order of the above list. Therefore it makes a
difference, if taxes are applied before or after having applied the shipping costs.

Moreover, whenever in the detail view the quantity of a product is updated, then all configured
modifiers are ran for that item. This allows the ``ItemModelSerializer``, to even change the unit
price of a product, depending on the total content of the cart.

Cart modifiers are easy to write and they normally consist only of a few lines of code. It is the
intention of **django-SHOP** to seed an eco-system for these kinds of plugins. Besides computing
the total, cart modifiers can also be used to sum up the weight, if the merchant's product models
specifies it.

Here is an incomplete list of some useful cart modifiers:


Generic Cart Modifiers
----------------------

These kinds of cart modifiers are applied unconditionally onto the cart. A typical instance is the
``DefaultCartModifier``, the ``CartIncludeTaxModifier`` or the ``CartExcludeTaxModifier``.


DefaultCartModifier
~~~~~~~~~~~~~~~~~~~

The :class:`shop.modifiers.default.DefaultCartModifier` is required for almost every shopping cart.
It handles the most basic calculations, ie. multiplying the items unit prices with the chosen
quantity. Since this modifier sets the cart item's line total, it must be listed as the first entry
in ``SHOP_CART_MODIFIERS``.


.. _reference/payment-cart-modifier:

Payment Cart Modifier
~~~~~~~~~~~~~~~~~~~~~

From these kinds of modifiers, only that for the chosen payment method is applied. Payment Modifiers
are used to add extra costs or discounts depending on the chosen payment method. By overriding the
method ``is_disabled`` a payment method can be disabled; useful to disable certain payments in case
the carts total is below a certain threshold.


.. _reference/shipping-cart-modifier:

Shipping Cart Modifier
~~~~~~~~~~~~~~~~~~~~~~

From these kinds of modifiers, only that for the chosen shipping method is applied. Shipping
Modifiers are used to add extra costs or discounts depending on chosen shipping method, the number
of items in the cart and their weight. By overriding the method ``is_disabled`` a shipping method
can be disabled; useful to disable certain payments in case the cart's total is below a certain
threshold or the weight is too high.


How Modifiers work
~~~~~~~~~~~~~~~~~~

Cart modifiers should extend the :class:`shop.modifiers.base.BaseCartModifier` class and extend one
or more of the given methods:

.. note:: Until version 0.2 of **django-SHOP**, the Cart Modifiers returned the amount and label
	for the extra item rows, and **django-SHOP** added them up. Since Version 0.3 cart modifiers
	must change the line subtotals and cart total themselves.

.. autoclass:: shop.modifiers.base.BaseCartModifier
   :members:


.. _djangocms-cascade: http://djangocms-cascade.readthedocs.org/en/latest/
.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders
.. _directives: https://docs.angularjs.org/guide/directive
.. _script templates: https://docs.angularjs.org/api/ng/directive/script
