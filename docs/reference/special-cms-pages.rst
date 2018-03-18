.. _reference/special-cms-pages:

=================
Special CMS Pages
=================

Besides the Catalog-, Cart- and Checkout Views, some pages must be accessed from already prepared
templates, which are shipped with this framework. These templates use the templatetag
``{% page_url %}`` shipped by **django-CMS** with some hard coded IDs. Unless we want to rewrite those
templates, we must provide a few special CMS pages, where we specify those page IDs.


Customer Self Registering Page
==============================

The **django-SHOP** framework offers a plugin, which offers a form, where customers can enter their
email address and a password. This plugin is named **Authentication** using the
*Rendered Form: Register User*.

Sometimes

self-registering

This page shall offer a form,
 This plugin


In the **Advanced Settings** of the CMS page handling this form, use ``shop-register-customer``
as the page ID.


Customer Details Page
=====================

This page shall offer a form, where a customer can enter his personal details, such as his or her
names, email address and whatever else is interesting for the merchant.
