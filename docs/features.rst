=============================
Unique Features of djangoSHOP
=============================


djangoSHOP requires to describe your products instead of prescribing prefabricated models
=========================================================================================


djangoSHOP plugs directly into djangoCMS
========================================
* Product detail pages may use all templatetags from djangoCMS, such as the ``{% placeholder ... %}``,
  the ``{% static_placeholder ... %}``, or other CMS tags.
* djangoSHOP does not presuppose categories to organize product list views. Instead djangoCMS
  pages can be specialized to handle product lists via a CMS app. This allows the merchant to
  organize products into categories, using the existing page hierarchy from the CMS. It also allows
  to offer single products from a CMS page, without requiring any category.

djangoSHOP uses the Django REST framework and hence does not require any Django View
====================================================================================
* Django Views are used to encapsulate the business logic of your products. Since djangoSHOP wants
  


* Every view is based on REST interfaces.

* Infinite scrolling and paginated listings use the same template.

* Views for cart, checkout etc. can be inserted into exiting pages.

* This means that one can navigate through products, add them to the cart, modify the cart, register himself as new customer (or proceed as guest), add his shipping information, pay via Stripe and view his past orders. Other Payment Service Providers can be added in a pluggable manner.

Every page in the shop: product-list, product-detail, cart, checkout-page, orders-list, order-detail etc. is part of the CMS and can be edited through the plugin editor. The communication between the client and these pages is done exclusively through REST. This has the nice side-effect, that the merchants shop implementation does not require any Django-View.

djangoSHOP is shipped with individual components for each task. These plugins then can be placed into any CMS placeholder using the plugin editor. Each of these plugins is shipped with their own overridable template, which can also be used as a stand-alone template outside of a CMS placeholder. Templates for bigger tasks, such as the Cart-View are granular, so that the HTML can be overridden partially.

Authentication is done through auth-rest, which allows to authenticate against a bunch of social networks, such as Google+, Facebook, GitHub, etc in a pluggable manner.

Moreover, the checkout process is based on a configurable finite state machine, which means that a merchant can adopt the shops workflow to the way he is used to work offline.

Client code is built using Bootstrap-3.3 and AngularJS-1.3. jQuery is required only for the backends administration interface. All browser components have been implemented as AngularJS directives, so that they can be reused between projects. For instance, my current merchant implementation does not have a single line of customized JavaScript.

This makes is very easy, even for non-programmers, to implement a shop. A merchant only has to adopt his product models, optionally the cart and order models, and override the templates.

