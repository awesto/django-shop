
=========================
Django-SHOP documentation
=========================

.. toctree::
    :maxdepth: 1
    :numbered:

    architecture
    features


Upgrading
=========
If you are upgrading from an earlier version, please be sure to read the
:ref:`release-notes`.


Tutorial
========

This tutorial shows how to setup a working e-commerce site with **django-SHOP** using the given
dependencies. The code required to setup this demo can be found in the example/myshop folder.

.. toctree::
	:maxdepth: 1
	:numbered:

	tutorial/intro
	tutorial/catalog-views
	tutorial/commodity-product
	tutorial/smartcard-product
	tutorial/polymorphic-product
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
    reference/inventory
    reference/catalog
    reference/search
    reference/filters
    reference/cascade-plugins
    reference/cart-checkout
    reference/cart-icon
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
    reference/settings
    reference/worker
    reference/docker


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


Django/Python compatibility table
=================================

===========  ===  ===  ====  ====  ===  ===  ===  ===  ===
django-SHOP  Django                     Python
-----------  -------------------------  ------------------
\            1.8  1.9  1.10  1.11  2.0  2.7  3.4  3.5  3.6
===========  ===  ===  ====  ====  ===  ===  ===  ===  ===
0.10.x        ✓    ✓    ⨯     ⨯     ⨯    ✓    ✓   ✓    ⨯
0.11.x        ⨯    ✓    ✓     ⨯     ⨯    ✓    ✓   ✓    ✓
0.12.x        ⨯    ⨯    ⨯     ✓     ⨯    ✓    ✓   ✓    ✓
0.13.x        ⨯    ⨯    ⨯     ✓     ⨯    ✓    ✓   ✓    ✓
===========  ===  ===  ====  ====  ===  ===  ===  ===  ===


Development and Community
=========================

.. toctree::
    :maxdepth: 1

    changelog
    release-notes/index
    faq
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

License
=======

**Django-SHOP** is licensed under the terms of the BSD license.
