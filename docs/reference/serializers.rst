.. _reference/serializers:

================
REST Serializers
================

Good application programming style is to strictly separate of *Models*, *Views* and *Controllers*.
In typical classic Django jargon, *Views* act as, what outsiders normally denote a controller.

*Controllers* can sometimes be found on the server and sometimes on the client. In **django-SHOP**
a significant portion of the controller code is written in JavaScript in the form of Angular
directives_.

Therefore, all data exchange between the *View* and the *Model* must be performed in a serializable
format, namely JSON. This allows us to use the same business logic for the server, as well as for
the client. It also means, that we could create native mobile apps, which communicate with a
web-application, without ever seeing a line of HTML code.

Moreover, since **django-SHOP** uses **django-CMS** to organize all available components, a classic
Django "View" does not make much sense anymore. Therefore, as we evolve our Model-View-Control
pattern into a modern web application, our REST serializers become the new controllers.


From a Database Model to the Serializer
=======================================

As we already know, all database models from the **django-SHOP** framework are owned by the merchant
implementation. Model serializers reflect their content and hence are tightly coupled with them.
We therefore must be able to create our own serializers in a way similar to how we extend our
database models. This means that we have a set of base serializers, which perform the task required
by their basic counterpart models. Thus, if we extend these models, we normally also might want to
extend their serializers.


Every URL is a REST endpoint
============================

Every URL which is part of part of **django-SHOP**, namely the product's list and detail views, the
cart and checkout views, the order list and detail views, they all are REST endpoints. What does
that mean?


Catalog List View
-----------------

Say, we are working with the provided demo shop, then the product's list view is available at
http://localhost:8000/de/shop/ . By appending ``?format=json`` to the URL, the raw data making up
our product list, is rendered as a JSON object. For humans, this is difficult to read, therefore
the Django Restframework offers a version which is more legible: Instead of the above, we invoke the
URL as http://localhost:8000/de/shop/?format=api . This renders the list of products as:

|rest-catalog-list|

.. |rest-catalog-list| image:: /_static/rest-catalog-list.png


Overriding the default Product Summary Serializer
.................................................


.. code-block:: python
	:caption: myshop/serializers.py
	:linenos:

	from shop.serializers.bases import ProductSerializer
	from myshop.models.product import MyProduct

	class ProductSummarySerializer(ProductSerializer):
	    class Meta:
	        model = MyProduct
	        fields = ['id', 'product_name', 'product_url',
	                  'product_type', 'product_model', 'price']

All these fields can be extracted directly from the product model with the exception of the sample
image. This is because we yet do not know the final dimensions of the image inside its HTML element
such as ``<img src="...">``, and we certainly want to resize it using easy-thumbnails_ with Pillow_
before it is delivered. An easy way to solve this problem is to use the ``SerializerMethodField``.
Simply extend the above class to:

.. code-block:: python
	:linenos:

	from rest_framework.serializers import SerializerMethodField

	class ProductSummarySerializer(ProductSerializer):
	    media = SerializerMethodField()

	    def get_media(self, product):
	        return self.render_html(product, 'media')

As you might expect, ``render_html`` assigns a HTML snippet to the field ``media`` in the serialized
representation of our product. This method uses a template to render the HTML. The name of this
template is constructed using the following rules:

#. Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` in lower
   case. If no such folder can be found, then use the folder named ``shop``.
#. Search for a subfolder named ``products``.
#. Search for a template named "*label*-*product_type*-*postfix*.html". These three subfieds are
   determined using the following rule:

   - *label*: the component of the shop, for instance ``catalog``, ``cart``, ``order``.
   - *product_type*: the class name in lower case of the product's Django model, for instance
     ``smartcard``, ``smartphone`` or if no such template can be found, just  ``product``.
   - *postfix*: This is an arbitrary name passed in by the rendering function. As in the example
     above, this is the string ``media``.

.. note:: It might seem *un*-RESTful to render HTML snippets by a serializer and deliver them via
	JSON to the client. However, we somehow must re-size the images assigned to our product to
	fit into the layout of our list view. The easiest way to do this in a configurable manner is
	to use the easy-thumbnails_ library and its templatetag
	``{% thumbnail product.sample_image ... %}``.

The template to render the media snippet could look like:

.. code-block:: django
	:caption: myshop/products/catalog-smartcard-media.html

	{% load i18n thumbnail djng_tags %}
	{% thumbnail product.sample_image 100x100 crop as thumb %}
	<img src="{{ thumb.url }}" width="{{ thumb.width }}" height="{{ thumb.height }}">

The template of the products list view then may contain a list iteration such as:

.. code-block:: django
	:emphasize-lines: 5

	{% for product in data.results %}
	  <div class="shop-list-item">
	    <a href="{{ product.product_url }}">
	      <h4>{{ product.product_name }}</h4>
	        {{ product.media }}
	        <strong>{% trans "Price" %}: {{ product.price }}</strong>
	    </a>
	  </div>
	{% endfor %}

The tag ``{{ product.media }}`` inserts the HTML snippet as prepared by the serializer from above.
A serializer may add more than one ``SerializerMethodField``. This can be useful, if the list view
shall render different product types using different snippet templates.



Catalog Detail View
-------------------

By following a URL of a product's detail view, say
http://localhost:8000/de/shop/smart-phones/apple-iphone-5?format=api , one may check the legible
representation such as:

|rest-catalog-detail|

.. |rest-catalog-detail| image:: /_static/rest-catalog-detail.png


Routing to these endpoints
--------------------------

Since we are using CMS pages to display the catalog's list view, we must provide an apphook_ which
must be attached to this page. Since these catalog apphooks can vary in many ways they are not part
of the shop framework, but must be created and added to the project as the
:ref:`reference/create-CatalogListApp`.


Catalog List View
.................

The urlpattern matching the regular expression ``^$`` routes onto the catalog list view class
:class:`shop.views.catalog.CMSPageProductListView` passing in a special serializer class, for
example :class:`myshop.serializers.ProductSummarySerializer`. This has been customized to represent
our product models in our catalog templates. Since the serialized data now is available as a Python
dictionary or as a plain Javascript object, these templates then can be rendered by the Django
template engine, as well as by the client using for instance AngularJS.

This View class, which inherits from :class:`rest_framework.generics.ListAPIView` accepts a list of
filters for restricting the list of items.

As we (ab)use CMS pages as categories, we somehow must assign them to our products. Therefore our
example project assigns a many-to-many field named ``cms_pages`` to our Product model. Using this
field, the merchant can assign each product to one or more CMS pages, using the apphook
``Catalog List``.

This special ``filter_backend``, :class:`shop.rest.filters.CMSPagesFilterBackend`, is responsible
for restricting selected products on the current catalog list view.


Catalog Detail View
...................

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
...................

The product detail view requires another serializer, the so called ``AddToCartSerializer``. This
serializer is responsible for controlling the number of items being added to the cart and gives
feedback on the subtotal of that potential cart item.

By appending the special string ``add-to-cart`` to the URL of a product's detail view, say
http://localhost:8000/de/shop/smart-phones/apple-iphone-5/add-to-cart?format=api , one may check
the legible representation of this serializer:

|rest-add-to-cart|

.. |rest-add-to-cart| image:: /_static/rest-add-to-cart.png

This serializer is slightly different than the previous ones, because it not only serializes
data and sends it from the server to the client, but it also deserializes data submitted from the
client back to the server using a post-request. This normally is the quantity, but in more
elaborated use cases, it also could contain attributes to distinguish product variations. The
``AddSmartPhoneToCartSerializer`` for example, uses this pattern.

Since we may create our own *Add this Product to Cart Serializer* for each product type in our shop,
hence overriding its functionality with a customized implementation, such a serializer may return
any other information relevant to the customer. This could for instance be a rebate or just an
update of the availability.


Cart and Checkout Views
-----------------------

CMS pages containing forms to edit the cart and the checkout views, do not require any URL routing,
because their HTML is rendered by the CMS plugin system, whereas form submissions are handled
by hard coded REST endpoints. These URLs are exclusively used by Ajax requests and never visible
in the URL line of our browser. Those endpoints are configured by adding them to the root resolver
at a project level:

.. code-block:: python
    :caption: myshop/urls.py
    :name: checkout-urls

    urlpatterns = [
        ...
        url(r'^shop/', include('shop.urls', namespace='shop')),
        ...
    ]

The serializers of the cart then can be accessed at http://localhost:8000/shop/api/cart/ ,
those of the watch-list at http://localhost:8000/shop/api/watch/ and those handling the various
checkout forms at http://localhost:8000/shop/api/checkout/ . Accessing these URLs can be useful,
specially when debugging JavaScript code.


Order List and Detail Views
---------------------------

The Order List and Detail Views must be accessible through a CMS page, therefore we need a speaking
URL. This is similar to the Catalog List View. This means that the Order Views require the apphook_
named "*View Orders*", which must be configured in the advanced settings of the Order's CMS pages.
This apphook is shipped with **django-SHOP** itself and can be found at ``shop/cms_apps.py``.

As with all other Views used by **django-SHOP**, the content of this View can also be rendered in
its dictionary structure, instead of HTML. Just append ``?format=api`` to the URL and get the Order
details. In our myshop example this may look like:

|rest-order-detail|

.. |rest-order-detail| image:: /_static/rest-order-detail.png


Search Result Views
-------------------

As with the Order View, also the Search Results View is accessible through a CMS page. Say, a
search query directed us to http://localhost:8000/en/search/?q=iphone , then the content of this
query can be made visible by adding ``&format=api`` to this URL and get the results in its
dictionary structure. This is specially useful to test if a customized search serializer returns
the expected results. In our myshop example this may look like:

|rest-search-results|

.. |rest-search-results| image:: /_static/rest-search-results.png


Final Note
==========

In previous versions of **django-SHOP**, these kinds of controller implementations had to be
implemented by customized Django View classes. This programming pattern led to bloated code,
because the programmer had to do a case distinction, whether the request was of type GET, POST
or some kind of Ajax. Now **django-SHOP** is shipped with reusable View classes, and the merchant's
implementation must focus exclusively on serializers. This is much easier, because it separates the
business logic from the underlying request-response-cycle.


.. _directives: https://docs.angularjs.org/guide/directive
.. _apphook: http://django-cms.readthedocs.org/en/stable/introduction/apphooks.html
.. _easy-thumbnails: https://easy-thumbnails.readthedocs.io/en/stable/
.. _Pillow: https://pillow.readthedocs.io/en/stable/
