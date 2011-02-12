============
Architecture
============

This document should gather all the pre-code architecture requirements/research.

Core system
===========

Generally, the shop system can be seen as two different phases, with two different problems to solve:

The shopping phase:
-------------------

From a user perspective, this is where you shop around different product categories, and add desired products to
a shopping cart (or other abstraction). This is a very well-know type of website problematic from a user interface
perspective as well as from a model perspective: a simple "invoice" pattern for the cart is enough.

The complexity here is to start defining what a shop item should be.

The checkout process:
---------------------

As the name implies, this is a "workflow" type of problem: we must be able to add or remove steps to the checkout process depending
on the presence or absence of some plugins.
For instance, a credit-card payment plugin whould be able to insert a payment details page with credit card details in the general workflow.

To solve this we could implement a workflow engine. The person implementing the webshop whould then define the process using
the blocks we provide, and the system should then "run on its own".


Random ideas:
-------------

* multiple shops (site and prefixed)

    * namespaced urls for shops 

        psuedocode , is this possible and or a good idea? requires restarts like the cms apphooks.

        .. code-block:: python

            prefix = shop.prefix
            # shopsite.get_urls(shop) # returns a tuple of (urlpatterns, app_name, shop_namespace)
            url(prefix, shopsite.get_urls(shop), kwargs={'shop_prefix': prefix})

        on a product

        .. code-block:: python

            def get_product_url(self):
               return reverse('shop_%s:product_detail' % threadlocals.shop_pk, kwargs={'category_slug': self.category_slug, slug=product.slug})

    * middleware to find current shop based on site and or prefix/ set current shop id in threadlocals?( process view )

        .. code-block:: python

            def process_view(self, request, view_func, view_args, view_kwargs)
                shop_prefix = view_kwargs.pop('shop_prefix', None):
                if shop_prefix:
                    shop = Shop.objects.get(prefix=shop_prefix)
                    request.shop = shop
                    threadlocals.shop_pk = shop.pk

* class-based views
* class based plugins (not modules based!)


Plugin structure
================

Plugins should be class based, as most of the other stuff in Django is (for instace the admins), with the framework
defining both a base class for plugin writers to extend, as well as a registration method for subclasses.

Proposal by fivethreeo for the plugin structure:

.. literalinclude:: snippets/modules.py
   :language: python

Similar to the Django-CMS plugins, most of the shop plugins will probably have to render templates (for instance when
they want to define a new checkout step).


.. _cart:

Shoppping Cart
==============

In its core this is a list of a kind of CartItems which relate to Product.

It should be possible to have the same Product in different CartItems
when some details are different. Stuff like different service addons
etc.


.. _prices:

Prices
======

This seems to be rather complex and must be pluggable. Prices may be
influenced by many different things like the Product itself,
quantities, the customer (location, special prices), shipping method
and the payment method. This all would have to be handled by special /
custom pricing implementations. The core implementation must only
include ways for such extension possibilities.

Prices will also be related to taxes in some way.

The core product implementation should possibly know nothing about
prices and taxes at all.

