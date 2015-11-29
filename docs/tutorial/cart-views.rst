==========
Cart Views
==========

In **djangoSHOP**, the cart view follows the same idea as all other pages – it is managed by the
CMS. Change into the Django admin backend and enter into CMS page tree.

Click onto the button **Add page** and add a page named “Cart”. Click onto **Advanced Settings**
at the bottom of the page. Chose a template which contains at least one placeholder_.

Optionally fill the input field named **Id** with the identifier “shop-cart”. This is required by
some templates which link directly onto the cart view page. If unset, these links will not work.

It is suggested to check the input field named **Soft root** to hide this pages from showing up
in the main menu bar. Presumably you prefer to use a special cart symbol located on the top right
of your pages to link onto this view. Otherwise a menu item named “Cart” will appear side by side
all the pages from the CMS.

Click onto **View on site** to change into front-end editing mode. Locate the main placeholder and
add a **Row** followed by a **Column** plugin from the section **Bootstrap**. Below that column add
a **Cart** plugin from section **Shop**. As rendering option chose **Editable Cart**, then publish
the page, it now should display an empty cart.


Editable Cart
-------------

An ‘Editable Cart’ is rendered using the Angular JS template engine. This means that a customer may
change the number of items, delete them or move them the the watch-list. Each update is reflected
immediately into the cart's subtotal, extra fields and final totals.


Static Cart
-----------

An alternative to the editable cart is the ‘static cart’. Here the cart items are rendered by
the Django template engine. Since here everything is static, the quantity can't be changed anymore
and the customer would have to proceed to the checkout without being able to change his mind. This
probably only makes sense when purchasing a single product.


Cart Summary
------------

This only displays the cart's subtotal, the extra cart fields, such as V.A.T. and shipping costs
and the final total.


Watch List
----------

A special view of the cart is the watch list. It can be used by customers to remember items they
want to compare or buy sometimes later. The watch-list by default is editable, but does not 
allow to change the quantity. This is because the watch-list shares the same object model as the
cart items. If the quantity of an item 0, then that cart item is considered to be watched. If
instead the quantity is 1 ore more, the item is considered to be in the cart. It therefore is
very easy to move items from the cart to the watch-list and vice versa. This concept also disallows
to have an item in both the cart and the watch-list. This during online shopping, often can be a
major point of confusion.


Change the templates
--------------------

The path of the templates used to render the cart views is constructed using the following rules:

* Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` in lower
  case. If no such folder can be found, then use the folder named ``shop``.
* Search for a subfolder named ``cart``.
* Search for a template named “editable.html”, “static.html”, “watch.html” or “summary.html”.

These templates are written to be easily extensible by the customized templates. To override the
‘editable cart’ add a template with the path, say ``myshop/cart/editable.html`` to the projects
template folder. This template then shall begin with ``{% extend "shop/cart/editable.html" %}``
and only override the ``{% block %}...{% endblock %}`` interested in.

Please note that cart items are rendered using an Angular JS `directive script template`_. It
therefore becomes very straight-forward to override Javascript templates using Djangos internal
template engine.


Proceed to Checkout
-------------------

On the cart's view, the designer using **djangoSHOP** may decide whether to combine the cart with
the checkout view, or to proceed onto a special checkout page. In the latter case simply add a
button to the cart, which links onto that checkout page. Otherwise add the CMS plugins required for
checkout right onto the cart view.

.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders
.. _directive script template: https://docs.angularjs.org/api/ng/directive/script
