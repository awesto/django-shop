.. _architecture:

=====================
Software Architecture
=====================

The **django-SHOP** framework is, as its name implies, a framework and not a software which runs
out of the box. Instead, an e-commerce site built upon **django-SHOP**, always consists of this
framework, a bunch of other Django apps and the **merchant's own implementation**. While this may
seem more complicate than a ready-to-use solution, it gives the programmer enormous advantages
during the implementation:

Not everything can be "explained" to a software system using graphical user interfaces. After
reaching a certain point of complexity, it normally is easier to pour those requirements into
executable code, rather than to expect yet another set of configuration buttons.

When evaluating **django-SHOP** with other e-commerce solutions, I therefore suggest to do the
following litmus test:

Consider a product which shall be sold world-wide. Depending on the country's origin of the request,
use the native language and the local currency. Due to export restrictions, some products can not
be sold everywhere. Moreover, in some countries the value added tax is part of the product's price,
and must be stated separately on the invoice, while in other countries, products are  advertised
using net prices, and tax is added later on the invoice.

Instead of looking for software which can handle such a complex requirement, rethink about writing
your own plugins, able to handle this. With the **django**, **REST** and **django-SHOP** frameworks,
this normally is possible in a few dozen lines of clearly legible Python code. Compare this to
solutions, which claim to handle such complex requirements. They normally are shipped containing
huge amounts of features, which very few merchants ever require, but which bloat the overall system
complexity, making such a piece of software expensive to maintain.


Design Decisions
================

Single Source of Truth
----------------------

A fundamental aspect of good software design is to follow the principle of "Don't repeat yourself",
often denoted as DRY. In **django-SHOP** we aim for a *single source of truth*, wherever possible.

For instance have a look at the :class:`shop.models.address.BaseShippingAddress`. Whenever we
add, change or remove a field, the ORM mapper of Django gets notified and with
``./manage.py makemigrations`` followed by ``./manage.py migrate`` our database scheme is updated.
But even the input fields of our address form adopt to all changes in our address model. Even the
client side form field validation adopts to every change in our address model. As we can see, here
our single source of truth is the address model.


Feature Completeness
--------------------

A merchant who wants to implement a unique feature for his e-commerce site, *must* never have to
touch the code of the framework. Aiming for ubiquity means, that no matter how challenging a feature
is, it *must be possible to be implemented* into the merchant's own implementation, rather than by
patching the framework itself.

Otherwise *this framework contains a bug* - not just a missing feature! I'm sure some merchants will
come up with really weird ideas, I never have thought of. If the **django-SHOP** framework inhibits
to add a feature, then feel free to create a bug report. The claim "*feature completeness*" for a
framework is the analogue to the term "*Turing completeness*" for programming languages.

Consider that on many sites, a merchant's requirement is patched into existing code. This means
that every time a new version of the e-commerce software is released, that patch must be repeatedly
adopted. This can become rather dangerous when security flaws in that software must be closed
immediately. **DjangoSHOP** instead is designed, so that the merchant's implementation and third
party plugins have to subclass its models and to override its templates accordingly.


Minimalism
----------

In a nutshell, **django-SHOP** offers this set of basic functionalities, to keep the framework
simple and stupid (KISS) without reinventing the wheel:

* A catalog to display product lists and detail views.
* Some methods to add products to the cart.
* A way to remove items from the cart or change their quantities.
* A set of classes to modify the cart's totals.
* A collection of forms, where customers can add personal, shipping and payment information.
* A way to perform the purchase: this converts the cart into an order.
* A list view where customers can lookup their previously performed orders
* A backend tool which helps to track the state of orders.

All functionality required to build a real e-commerce site, sits on top of this. Computing taxes
for instance, can vary a lot among different legislations and thus is not part of the framework.
The same applies for vouchers, rebates, delivery costs, etc.

These are the parts, which must be fine tuned by the merchant. They can be rather complicate to
implement and are best implemented by separate plugins.


Separation of Concern
---------------------

Compared to other e-commerce solutions, the **django-SHOP** framework has a rather small footprint
in terms of code lines, database tables and classes. This does not mean, that its functionality is
somehow limited. Instead, the merchant's own implementation can become rather large. This is
because **django-SHOP** implies dependencies to many third party Django apps.

Having layered systems gives us programmers many advantages:

* We don't have to reinvent the wheel for every required feature.
* Since those dependencies are used in other applications, they normally are tested quite well.
* No danger to create circular dependencies, as found often in big libraries and stand alone
  applications.
* Better overview for newcomers, which part of the system is responsible for what.
* Easier to replace one component against another one.

Fortunately Django gives us all the tools to stitch those dependencies together. If for instance we
would use one of the many PHP-based e-commerce system, we'd have to stay inside their modest
collection for third party apps, or reinvent the wheel. This often is a limiting factor compared to
the huge ecosystems arround Django.


Inversion of Control
--------------------

Wherever possible, **django-SHOP** tries to delegate the responsibility for taking decision to the
merchant's implementation of the site. Let explain this by a small example: When the customer
adds a product to the cart, **django-SHOP** consults the implementation of the product to determine
whether the given item is already part of the cart or not. This allows the merchant's implementation
to fine tune its product variants.


Core System
===========

Generally, the shop system can be seen in three different phases:


The shopping phase
------------------

From a customers perspective, this is where we look around at different products, presumably in
different categories. We denote this as the catalog list- and catalog detail views. Here we browse,
search and filter for products. In one of the list views, we edit the quantity of the products to
be added to our shopping cart.

Each time a product is added, the cart is updated which in turn run the so named "Cart Modifiers".
Cart modifiers sum up the line totals, add taxes, rebates and shipping costs to compute the final
total. The Cart Modifiers are also during the checkout phase (see below), since the chosen shipping
method and destination, as well as the payment method may modify the final total.


The checkout process
--------------------

Here the customer must be able to refine the cart' content: Change the quantity of an item, or remove
that item completely from the cart.

During the checkout process, the customer must enter his addresses and payment informations. These
settings may also influence the cart's total.

The final step during checkout is the purchase operation. This is where the cart's content is
converted into an order object and emptied afterwards.


The fulfillment phase
---------------------

It is now the merchants's turn to take further steps. Depending on the order status, certain
actions must be performed immediately or the order must be kept in the current state until some
external events happen. This could be a payment receivement, or that an ordered item arrived in
stock. While setting up a **django-SHOP** project, the allowed status transitions for the fulfillment
phase can be plugged together, giving the merchant the possibility to programmatically define his
order workflows.


Plugins
=======

Django SHOP defines 5 types of different plugins:

#. Product models
#. Cart modifiers
#. Payment backends
#. Shipping backends
#. Order workflow modules

They may be added as a third party **django-SHOP** plugin, or integrated into the merchant's
implementation.
