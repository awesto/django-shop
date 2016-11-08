
=========================
Django SHOP documentation
=========================

This is the documentation starting from version 0.9; if you are looking for the documentation of
django-shop version 0.2, please check the sidebar of RTD.

Version 0.9 of **django-SHOP** is a complete rewrite of the code base, keeping the concepts of model
overriding and cart modifiers. With some effort it should be possible to migrate existing projects
to this new release.

.. toctree::
    :maxdepth: 1
    :numbered:

    architecture
    features


Upgrading
=========
If you are upgrading from an earlier version, please be sure to read the
:doc:`upgrade instructions <upgrading>`.


Tutorial
========

This tutorial shows how to setup a working e-commerce site with **django-SHOP** using the given
dependencies. The code required to setup this demo can be found in the example/myshop folder.

.. toctree::
    :maxdepth: 1
    :numbered:

    tutorial/intro
    tutorial/quickstart
    tutorial/simple-product
    tutorial/multilingual-product
    tutorial/polymorphic-product
    tutorial/catalog-views
    tutorial/cart-checkout


Reference
==========

Reference to classes and concepts used in **django-SHOP**

.. toctree::
    :maxdepth: 1
    :numbered:

    reference/customer-model
    reference/deferred-models
    reference/money-types
    reference/product-models
    reference/catalog
    reference/search
    reference/filters
    reference/cascade-plugins
    reference/cart-checkout
    reference/payment-providers
    reference/order
    reference/delivery
    reference/addresses
    reference/notifications
    reference/serializers
    reference/client-framework
    reference/configuration
    reference/shipping-providers
    reference/special-cms-pages
    reference/cart-icon


How To's
========

Some recipes on how to perform certain tasks in **django-SHOP**.

*This collection of recipes unfortunately is not finished yet.*

.. toctree::
    :maxdepth: 1
    :numbered:

    howto/customize-snippets
    howto/handling-discounts
    howto/handling-taxes

Development and Community
=========================

.. toctree::
    :maxdepth: 1

    changelog
    upgrading
    contributing
    authors

To be written
=============

.. toctree::
    :maxdepth: 1

    howto/address-model
    howto/how-to-payment
    howto/multi-tenancy
    howto/secure-catalog

Obsolete documentation
======================

This documentation is only kept arond for historical reasons, please do not use
it.

.. toctree::
    :maxdepth: 1

    plugins
    settings
    various-ideas

License
=======

**Django-SHOP** is licensed under the terms of the BSD license.
