.. _faq:

============================
Frequently Asquest Questions
============================


Frontend Editing
================

Order Plugin
------------

**Editing the Order Plugin seems to be broken**

This has to do with the way, **django-CMS** handles the placeholder in its templates. Here the
problem is, that we're using the same template for both, the Order List View and their Detail
Views. The Order Detail Views however, are not managed by the CMS, but rather by a CMSApphook.
The latter confuses the CMS placeholder. It therefore is *strongly recommended* to edit the Order
Page only while in List View Mode.

JavaScript
----------

**Can I use django-SHOP without AngularJS?**

When using REST, then client side actions have to be handles somehow using JavaScript.
AngularJS was chosen in 2014, because it was the only MVVM-ish framework at the time. However,
the intention always has been, that merchants implementing their e-commerce site on top of
**django-SHOP** do not have to write a single line of code in JavaScript. The idea is, that
everything shall be adoptable using the special HTML elements introduced by **django-SHOP**.

Unless all these directives are replaced by another JavaScript framework, such as React, Ember,
Vue.js, Angular2/4, Aurelia, etc., one can setup **django-SHOP** without any JavaScript at all.
Then however, a lot of functionality is lost and the user experience will be modest.


CMS pages as categories
-----------------------

**My products have a many-to-many relation with the CMS PageModel. However, in the admin for the
product, the multi-select widget dos not show any pages.**

In the product's admin view, only CMS pages which in their advanced settings are marked as
``CatalogList``, are eligible to be connected with a product.
