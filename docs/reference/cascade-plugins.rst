.. _cascade-plugins:

===========
CMS Plugins
===========

**DjangoSHOP** extends the eco-system for **djangoCMS**, djangocms-cascade_, by some shop-specific
plugins. This allows the merchant of a shop-site, to exclusively use CMS pages for every possible
step during the purchasing procedure.


Cart
====

The Cart plugin has already been described in detail in this tutorial. Often a summary of the cart
is shown at the end of the checkout process. Here a static cart often is useful.


Customer Form
=============

This form is used to query information about the customer, such as salutation, the first and last
names, its email address etc. In simple terms this form combines the fields from the models
``User`` and ``Customer``. Since **djangoSHOP** honors the principle of `Single Source of Truth`_,
if extra fields are added to the Customer model, no additional action is required by the programmer.
This means that changes to our model fields, are reflected automatically into this rendered customer
form.

.. _Single Source of Truth: https://en.wikipedia.org/wiki/Single_Source_of_Truth


Guest Form
==========

