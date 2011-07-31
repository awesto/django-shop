============
Templatetags
============

django-shop ships various templatetags to make quick creation of HTML templates
easier. In order to use these templatetags you need to load them in your
template

.. highlight:: html+django

::

  {% load shop_tags %}

Cart
====

Renders information about the Cart object. This could be used (for example) to
show the total amount of items currently in the cart on every page of your shop.

Usage
-----

::

  {% load shop_tags %}
  {% cart %}

In order to define your own template, override the template
``shop/templatetags/_cart.html``. The tag adds a variable called ``cart`` to
the context.

Order
=====

Renders information about an Order object.

Usage
-----

::

  {% load shop_tags %}
  {% order my_order %}

In order to define your own template, override the template
``shop/templatetags/_order.html``. The tag adds a variable called ``order`` to
the context.

Product
=======

Renders information about all active products in the shop. This is useful if
you need to display your products on pages other than just ``product_list.html``.

Usage
-----

If no argument is given, the tag will just render all active products. The tag
allows an optional argument ``objects``. It should be a queryset of
:class:`~shop.models.Product` objects. If given, the tag will render the given
products only instead of all active products.

::

  {% load shop_tags %}
  {% products %}
  {% products object_list %}

In order to define your own template, override the template
``shop/templatetags/_products.html``. The tag adds a variable called
``products`` to the context.
