.. _features:

==============================
Unique Features of django-SHOP
==============================


django-SHOP requires to describe your products instead of prescribing prefabricated models
==========================================================================================

Products can vary wildly, and modeling them is not always trivial. Some products are salable in
pieces, while others are continues. Trying to define a set of product models, capable for describing
all such scenarios is impossible – describe your product by customizing the model and not vice
versa.


E-commerce solutions, claiming to be plug-and-play, normally use one of these (anti-)patterns
---------------------------------------------------------------------------------------------

Either, they offer a field for every possible variation, or they use the Entity-Attribute-Value
pattern to add meta-data for each of your models. This at a first glance seems to be easy. But both
approaches are unwieldy and have serious drawbacks. They both apply a different "physical schema" –
the way data is stored, rather than a "logical schema" – the way users and applications require that
data. As soon as you have to combine your e-commerce solution with some Enterprise-Resource-Planning
software, additional back-and-forward conversion routines have to be added.


In django-SHOP, the physical representation of a product corresponds to its logical
-----------------------------------------------------------------------------------

**django-SHOP**'s approach to this problem is to have minimal set of models. These abstract models
are stubs provided to subclass the physical models. Hence the logical representation of the
product conforms to their physical one. Moreover, it is even possible to represent various types of
products by subclassing polymorphically from an abstract base model. Thanks to the Django framework,
modeling the logical representation for a set of products, together with an administration backend,
becomes almost effortless.


Django-SHOP is multilingual
===========================

Products offered in various regions, normally require attributes in different natural languages.
For such a set of products, these attributes can be easily modelled using translatable fields.
This lets you seamlessly built a multilingual e-commerce site.


Django-SHOP supports multiple currencies
========================================

Django-SHOP is shipped with a set of currency types, bringing their own money arithmetic. This
adds an additional layer of security, because one can not accidentally sum up different currencies.
These money types always know how to represent themselves in different local environments, prefixing
their amount with the correct currency symbol. They also offer the special amount "no price"
(represented by ``–``), which behaves like zero but is handy for gratuitous items.


Django-SHOP directly plugs into django-CMS
==========================================

Product detail pages may use all templatetags from **django-CMS**, such as the ``{% placeholder ... %}``,
the ``{% static_placeholder ... %}``, or other CMS tags.

**Django-SHOP** does not presuppose categories to organize product list views. Instead django-CMS
pages can be specialized to handle product lists via a CMS app. This allows the merchant to organize
products into categories, using the existing page hierarchy from the CMS. It also allows to offer
single products from a CMS page, without requiring any category.


Django-SHOP is based on REST
============================

* Django-SHOP uses the Django REST framework and hence does not require any Django View
* Every view is based on REST interfaces.
* Infinite scrolling and paginated listings use the same template.
* Views for cart, checkout etc. can be inserted into exiting pages.
* This means that one can navigate through products, add them to the cart, modify the cart, register
  himself as new customer (or proceed as guest), add his shipping information, pay via Stripe and
  view his past orders. Other Payment Service Providers can be added in a pluggable manner.

Every page in the shop: product-list, product-detail, cart, checkout-page, orders-list, order-detail
etc. is part of the CMS and can be edited through the plugin editor. The communication between the
client and these pages is done exclusively through REST. This has the nice side-effect, that the
merchants shop implementation does not require any Django-View.

Django-SHOP is shipped with individual components for each task. These plugins then can be placed
into any CMS placeholder using the plugin editor. Each of these plugins is shipped with their own
overridable template, which can also be used as a stand-alone template outside of a CMS placeholder.
Templates for bigger tasks, such as the Cart-View are granular, so that the HTML can be overridden
partially.

Authentication is done through auth-rest, which allows to authenticate against a bunch of social
networks, such as Google+, Facebook, GitHub, etc in a pluggable manner.

Moreover, the checkout process is based on a configurable finite state machine, which means that a
merchant can adopt the shops workflow to the way he is used to work offline.

Client code is built using Bootstrap-3.3 and AngularJS-1.3. jQuery is required only for the backends
administration interface. All browser components have been implemented as AngularJS directives, so
that they can be reused between projects. For instance, my current merchant implementation does not
have a single line of customized JavaScript.

This makes it very easy, even for non-programmers, to implement a shop. A merchant only has to adopt
his product models, optionally the cart and order models, and override the templates.

