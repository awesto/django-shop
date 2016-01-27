.. _cascade-plugins:

===============
Cascade Plugins
===============

**DjangoSHOP** extends the eco-system of **djangoCMS** plugins, djangocms-cascade_, by additional
shop-specific plugins. This allows the merchant to use CMS pages in all possible circumstances.


Cart
====

The **CartPlugin** has four different rendering options: Editable, Static, Summary and Watch-List.
The :ref:`cart-cascade-plugin` has already been described in detail.


Customer Form
=============

The **CustomerFormPlugin** is used to query information about the customer, such as salutation,
the first- and last names, its email address etc. In simple terms this form combines the fields
from the model classes ``User`` and ``Customer``. Since **djangoSHOP** honors the principle of
`Single Source of Truth`_, if extra fields are added to the Customer model, no additional action is
required by the programmer. This means that changes to our model fields, are reflected automatically
into this rendered customer form.


Guest Form
==========

The **GuestFormPlugin** is a reduced version of the customer form. It just takes the email address,
but nothing else.


Address Forms
=============

There are two address form plugins, **ShippingAddressFormPlugin** and **BillingAddressFormPlugin**.
They both offer a form which is derived from the materialized ``shop.models.address.AddressModel``.


Select a Payment Provider
=========================

For each payment provider registered with the shop, the **PaymentMethodFormPlugin** creates a list
of radio buttons, where customers can chose their desired payment provider. By overriding the
rendering templates, additional forms, for instance to add credit card data, can be added.


Select a Shipping Method
========================

For each shipping provider registered with the shop, the **ShippingMethodFormPlugin** creates a list
of radio buttons, where customers can chose their desired shipping method.


Extra Annotations
=================

The **ExtraAnnotationFormPlugin** shall be used to give customers the opportunity to enter an
arbitrary text message, during the checkout process.


Accept Conditions
=================

Almost always customers must click onto a checkbox to various legal requirements, such as accepting
the terms and conditions of the shop. The **AcceptConditionFormPlugin** offers an editor, where the
merchant can enter some text together with a link onto a page with more detailed explanations.


Authentication
==============

The **ShopAuthenticationPlugin** can be used to render forms used in various authentication
contexts such as:

* A simple login form
* Login forms with possibility to reset the password
* Logout Button
* Login form which switches into a logout button, for authenticated customers
* A form to reset the password
* A form to change the password
* A form for unknown customers to register themselves
* A forms, so that customers can declrae themselves as guests


Catalog
=======

The catalog list view is handled by the **ShopCatalogPlugin**.

This plugin requires a CMS page, which uses the CMSApp **ProductsListApp**. This app must be
implemented by the merchant and is part of the shop project.


Viewing Orders
==============

The **ShopOrderViewsPlugin** is used to render the list- and detail views of orders, specific to the
currently logged in customer. Without a number in the URL, a list of all orders is shown. By
adding the primary key to the URL, all ordered items from that specific order are shown.

This plugin requires a CMS page, which uses the CMSApp **OrderApp**. This app is part of the shop
framework and loaded automatically.


Overriding Templates
====================

For all plugins described here, the merchant can override the provided templates with their own
implementation. If the shop framework provides a template, named ``/shop/folder/template.html``,
then the merchant may override this template using ``/merchantimplementaion/folder/template.html``.

This template then usually extends the existing framework template with

.. code-block:: django

	{% extends "/shop/folder/template.html" %}
	
	{% block shop-some-identifier %}
	    <div>...</div>
	{% endblock %}

.. _djangocms-cascade: http://djangocms-cascade.readthedocs.org/en/latest/
.. _Single Source of Truth: https://en.wikipedia.org/wiki/Single_Source_of_Truth
