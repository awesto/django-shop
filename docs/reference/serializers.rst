.. _serializers:

================
REST Serializers
================

God application programming style is to strictly separate of *Models*, *Views* and *Controllers*.
In typical classic Django jargon, *Views* act as, what outsiders normally would denote a controller.

Controllers can sometimes be found on the server and sometimes on the client. In **djangoSHOP**
a significant portion of the controller code is written in JavaScript in the form of Angular
directives_.

Therefore, all data exchange between the *View* and the *Model* must be performed in a serializable
format, namely JSON. This allows us to use the same business logic for the server, as well as for
the client. It also means, that we could create native mobile apps, which communicate with a
web-application, without ever seeing a line of HTML code.


Every URL is a REST endpoint
============================

Every URL which is part of part of **djangoSHOP**, namely the product's list and detail views, the
cart and checkout views, the order list and detail views, they all are REST endpoints. What does
that mean?


Catalog List View
-----------------

Say, you are working with the provided demo shop, then the product's list view is available at
http://localhost:8000/de/shop/ . By appending ``?format=json`` to the URL, the raw data making up 
our product list, is rendered as a JSON object. For humans, this is difficult to read, therefore
the Django Restframework offers a version which is more legible: Instead of the above, invoke the
URL as http://localhost:8000/de/shop/?format=api . This renders the list of products as:

|rest-catalog-list|

.. |rest-catalog-list| image:: /_static/rest-catalog-list.png


Catalog Detail View
-------------------

By following a URL of a product's detail view, say
http://localhost:8000/de/shop/smart-phones/apple-iphone-5?format=api , one may check the legible
representation such as:

|rest-catalog-detail|

.. |rest-catalog-detail| image:: /_static/rest-catalog-detail.png


Add Product to Cart
-------------------

The product detail view requires another serializer, the so called ``AddToCartSerializer``. This
serializer is responsible for controlling the number of items being added to the cart and gives 
feedback on the subtotal of that potential cart item.

This serializer is slightly different than the previous ones, because it not only serializes
data and sends it from the server to the client, but it also deserializes data submitted from the
client back to the server using a post-request. This normally is the quantity, but in more
elaborated use cases, this could contain attributes to distinguish product variations. The
``AddSmartPhoneToCartSerializer``uses this pattern.

Since each product type may inherit from ``AddToCartSerializer``, and hence override its
functionality with a customized implementation, such a serializer may return any other information
relevant to the customer. This could for instance be a rebate or an availability update.


Routing to these endpoints
--------------------------

Since we are using CMS pages to display the catalog's list view, we must provide an apphook_ to
attach it to this page. These catalog apphooks are not part of the shop framework, but must be
created and added to the project:

.. code-block:: python
	:caption: myshop/cms_app.py

	from cms.app_base import CMSApp
	from cms.apphook_pool import apphook_pool

	class CatalogListApp(CMSApp):
	    name = "Catalog List"
	    urls = ['myshop.urls.catalog']

	apphook_pool.register(CatalogListApp)

We now must add routes for all sub-URLs of the given CMS page implementing the catalog list:

.. code-block:: python
	:caption: myshop/urls/catalog.py

	from django.conf.urls import patterns, url
	from rest_framework.settings import api_settings
	from shop.rest.filters import CMSPagesFilterBackend
	from shop.views.catalog import (AddToCartView, ProductListView,
	    ProductRetrieveView)
	from myshop.serializers import (ProductSummarySerializer,
	    ProductDetailSerializer)

	urlpatterns = patterns('',
	    url(r'^$', ProductListView.as_view(
	        serializer_class=ProductSummarySerializer,
	        filter_backends=api_settings.DEFAULT_FILTER_BACKENDS + [
	            CMSPagesFilterBackend()],
	    )),
	    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(
	        serializer_class=ProductDetailSerializer,
	    )),
	    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()
	    ),
	)


Products List View
~~~~~~~~~~~~~~~~~~

The urlpattern matching the regular expression ``^$`` routes onto the catalog list view class
:class:`shop.views.catalog.ProductListView` passing in a special serializer class,
:class:`myshop.serializers.ProductSummarySerializer`. This has been customized to represent our
product models in our catalog templates. Since the serialized data now is available as a Python
dictionary or as a Plain Old Javascript Object, these templates then can be rendered by the Django
template engine, as well as by the client using for instance AngularJS.

This View class, which inherits from :class:`rest_framework.generics.ListAPIView` accepts a list of
filters for restricting the list of items.

As we (ab)use CMS pages as categories, we somehow must assign them to our products. Therefore our
example project assigns a many-to-many field named ``cms_pages`` to our Product model. Using this
field, the merchant can assign each product to one or more CMS pages, using the apphook
``Products List``.

This special ``filter_backend``, :class:`shop.rest.filters.CMSPagesFilterBackend`, is responsible
for restricting selected products on the current catalog list view.


Product Detail View
~~~~~~~~~~~~~~~~~~~

The urlpattern matching the regular expression ``^(?P<slug>[\w-]+)$`` routes onto the class
:class:`shop.views.catalog.ProductRetrieveView` passing in a special serializer class,
:class:`myshop.serializers.ProductDetailSerializer` which has been customized to represent our
product model details.

This View class inherits from :class:`rest_framework.generics.RetrieveAPIView`. In addition to the
given ``serializer_class`` it can accept these fields:

* ``lookup_field``: Model field to look up for the retrieved product. This defaults to ``slug``.
* ``lookup_url_kwarg``: URL argument as used by the matching RegEx. This defaults to ``slug``.
* ``product_model``: Restrict to products of this type. Defaults to ``ProductModel``.


Add Product to Cart
~~~~~~~~~~~~~~~~~~~


Annotation
----------

In previous versions of **djangoSHOP**, this kind of controller implementation had to be implemented
inside the 

This meand that 
Since the serialized data now is available as a Python
dictionary or as a Plain Old Javascript Object, these templates then can be rendered server-side,
as well as by a client-side template engine.


.. _directives: https://docs.angularjs.org/guide/directive
.. _apphook: http://django-cms.readthedocs.org/en/stable/introduction/apphooks.html
