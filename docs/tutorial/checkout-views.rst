==============
Checkout Views
==============

In **djangoSHOP**, the checkout view follows the same idea as all other pages – it is managed by
the CMS. Change into the Django admin backend and enter into CMS page tree. A good position in
that tree for adding the Checkout page is just below the Cart page. Then as the template, you can
use “Inherit from parent”.

The Checkout page is probably the most complicated page to setup. Therefore no generic receipt
can be presented here. Instead some CMS plugins will be listed here. They can be useful to compose
a complete checkout page:

A list of plugins specific to **djangoSHOP** can be found in the reference section. They include
a cart editor, forms to enter the customers names, addresses, payment- and shipping methods, credit
card numbers and some more.

Other useful plugins can be found in the Django application djangocms-cascade_.


Scaffolding
===========

Depending on who is allowed to buy products, keep in mind that pure visiting customers must
declare themselves, whether they want to buy as guests or as registered users. This means that
we first must distinguish between pure visitors and recognized customers. The simplest way to do
this is to use the Segmentation **if**- and **else**-plugins. A recognized customer shall
be able to proceed directly to the purchasing page. A visiting customer first must declare himself,
this could be handled with a collections of plugins, such as:

|checkout-visitor|

.. |checkout-visitor| image:: /_static/checkout/visitor.png

in structure mode. This collection of plugins then will be rendered as:

|checkout-register|

.. |checkout-register| image:: /_static/checkout/register.png

Please note that the Authentication plugins **Login & Reset**, **Register User** and
**Continue as guest** must reload the current page. This is because during these steps a new
session-id is assigned, which is requires a full page reload.

After reloading the page, the customer is considered as “recognized”. Since there are a few forms
to be filled, this example uses a **Process Bar** plugin, which emulates a few sub-pages, which then
can be filled out by the customer step-by-step.

|checkout-recognized|

.. |checkout-recognized| image:: /_static/checkout/recognized.png

A fragment of this collection of plugins then will be rendered as:

|checkout-checkout|

.. |checkout-checkout| image:: /_static/checkout/checkout.png

.. _djangocms-cascade: http://djangocms-cascade.readthedocs.org/en/latest/