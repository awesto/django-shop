.. _tutorial/cart-checkout:

=================
Cart and Checkout
=================

In **django-SHOP**, the cart and checkout view follow the same idea as all other pages – they are
managed by the CMS. Change into the Django admin backend and look for the CMS page tree. A good
position for adding a page is the root level, but then assure that in Advanced Setting the checkbox
**Soft root** is set.

The checkout can be combined with the cart on the same page or moved on a separate page. Its best
position normally is just below the Cart page.

|static-cart|

.. |static-cart| image:: /_static/cart/static-cart.png

The Checkout pages presumably are the most complicated page to setup. Therefore no generic receipt
can be presented here. Instead some CMS plugins will be listed here. They can be useful to compose
a complete checkout page. In the reference section it is shown in detail how to create a
:ref:`reference/cart-checkout` view, but for this tutorial the best way to proceed is to have a look
in the prepared demo project for the *Cart* and *Checkout* pages.

A list of plugins specific to **django-SHOP** can be found in the reference section. They include
a cart editor, a static cart renderer, forms to enter the customers names, addresses, payment- and
shipping methods, credit card numbers and some more.

Other useful plugins can be found in the Django application djangocms-cascade_.


Scaffolding
===========

Depending on who is allowed to buy products, keep in mind that visitors must
declare themselves whether they want to buy as guest or as registered user. This means that
we first must distinguish between visitor and recognized customer. The simplest way to do
this is to use the Segmentation **if**- and **else**-plugin. A recognized customer shall
be able to proceed directly to the purchasing page. A visitor first must declare himself,
this could be handled with a collections of plugins, such as:

|checkout-visitor|

.. |checkout-visitor| image:: /_static/checkout/visitor.png

in structure mode. This collection of plugins then will be rendered as:

|checkout-register|

.. |checkout-register| image:: /_static/checkout/register.png

Please note that the Authentication plugins **Login & Reset**, **Register User** and
**Continue as guest** must reload the current page. This is because during these steps a new
session-id is assigned, which requires a full page reload.

After reloading the page, the customer is considered as "recognized". Since there are a few forms
to be filled, this example uses a **Process Bar** plugin, which emulates a few sub-pages, which then
can be filled out by the customer step-by-step.

|checkout-recognized|

.. |checkout-recognized| image:: /_static/checkout/recognized.png

A fragment of this collection of plugins then will be rendered as:

|checkout-checkout|

.. |checkout-checkout| image:: /_static/checkout/checkout.png

.. _djangocms-cascade: http://djangocms-cascade.readthedocs.org/en/latest/
