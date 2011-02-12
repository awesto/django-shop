

================================
 Requirements / Usage Scenarios
================================

This has been startet as an unorderet list of various requirements and
usage scenarios which may have an impact to the core
implementation. There are also some Items, which should not have an
impact on the core implementation.

The goal of this list is to sort out stuff which should be done in
some kind of extension package or app on their own.

This list will have to be sorted in some way to (hopefully) become
useful imput.


Core Stuff
==========

i18n
----

Most models need to be translatable.


Products
--------

Shops normally sell some kind of product. These products may be very
differnt, so the trick here is to stay very flexible and
extensible.

See :ref:`products` for current discussion details.


Catalog and Categories
----------------------

Shops are often organized by some kind of Category
implementation. Products may be assosiated to one (or multiple)
categories in which they should be shown.

Should Products know anything about Categories?

Alternatives may be to organize products by tags.

Categories should be implemented as an efficient tree (mptt).


Customers
---------

Is a Customer always a User?

Can Organisations be Customers?

Should Customers be Contacts with a special role?


Cart
----

Should be rather simple: A list of products.

See also :ref:`cart`


Orders
------

During the checkout process a Cart is transformed into an Order
(?). In pseudocode this would look like this::

   my_order = checkout(my_cart)

(``checkout()`` is the complicated part here)

An Order needs to contain copies of some data in case the referred
items change. Kind of historical data. Cases:

* price changes
* customer address changes
* ...

An Order also contains prices. The Cart itself does not need to
contain price information. (?)


Prices
------

Prices may get rather complicated.

See also :ref:`prices` for some generic notes.






Should have no impact to core
=============================



CMS-Integration
---------------

Every shop also contains some sort of pages which should be managed by
a CMS.

Important: Integration of navigation.

This should be implemented in its own app.


Image handling
--------------

Some models (e.g. Product, Category) may will have images attached to
them.

The handling of images (most often scaling) can be done by template
tags like sorl does. This should have no impact on core models and
left to the shop implementor.


Connectors to other systems
---------------------------

Shops may be seen as a frontent to ERP-Systems and should sometimes be
connected to these systems. It may also be possible that product data
should be taken from external sources and be processed by the shop
system.

These extensions should only use the core models but not influence
them in any kind. Meta-Information which may be required could be
stored well in their own models which contain a relativ to the basic
Product model (or other core models).

When data should be propagated outbound, they can attach
signal-handlers to appropriate signals.

It may be appropriate to add some general patterns / best practices to
the docs.


Whishlists
----------

Although this is a common shop feature, this can be seen as a generic
kind of "bookmark list" which contains a list of django models.


Notifications
-------------

Outbound notifications of nearly any kind could be implemented by
using appropriate signals of core models. So this should have not too
much influence to core stuff.

Use Cases:

* New Orders
* Order changes
* Product available in stock again
* ...

Maybe some custom signals should provided here.


Comments
--------

They are just available as a very generic app, nothing to be done here. (?)


