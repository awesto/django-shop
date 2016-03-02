.. _tutorial/catalog-views:

=============
Catalog Views
=============

Now that we know how to create product models and how to administer them, lets have a look on how
to route them to our views.

When editing the CMS page used for the products list view, open **Advanced Settings** and chose
**Products List** from the select box labeled **Application**.

Then chose a template with at least one placeholder_. Click onto **View on site** to change into
front-end editing mode. Locate the main placeholder and add a **Row** followed by a **Column**
plugin from the section **Bootstrap**. Below that column add a **Catalog List Views** plugin from
section **Shop**. Then publish the page, it should not display any products yet.

.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html
.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders


Add products to the category
----------------------------

Open the detail view of a product in Django's administration backend. Locate the many-to-many
select box labeled **Categories > Cms pages**. Select the pages where each product shall appear
on.

On reloading the list view, the assigned products now shall be visible. Assure that they have been
set to be active, otherwise they won't show up.

If you nest categories, products assigned to children will be also be visible on their parents
pages.


Product Model Serializers
=========================

We already learned how to write model classes and model managers, so what are serializers for?

In **djangoSHOP** the response views do not distinguish whether the product's information shall
be rendered as HTML or transferred via JSON. This gives us the ability to use the same business
logic for web browsers rendering static HTML, single page web applications communicating via AJAX
or native shopping applications for your mobile devices. This btw. is one of the great benefits
when working with RESTful_ API's and thanks to the djangorestframework_ we don't even have to
write any Django Views anymore.

For instance, try to open the list- or the detail view of any of the products available in the
shop. Then in the browsers URL input field append ``?format=api`` or ``?format=json`` to the URL.
This will render the pure product information, but without embedding it into HTML.

The REST API view is very handy while developing. If you want to hide this on your production
system , then in your settingy.py remove ``'rest_framework.renderers.BrowsableAPIRenderer'`` from 
``REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']``.

In the shop's catalog, we need some functionality to render a list view for all products and
we need a detail view to render each product type. The **djangoSHOP** framework supplies two
such serializers:


Serialize for the Products List View
------------------------------------

For each product we want to display in a list view, we need a serializer which converts the content
of the most important fields of a product. Normally these are the Id, the name and price, the URL
onto the detail view, a short description and a sample image.

The **djangoSHOP** framework does not know which of those fields have to be serialized, therefore
it requires some help from the programmer:

.. code-block:: python
	:caption: myshop/product_serializers.py
	:linenos:

	from shop.rest.serializers import ProductSummarySerializerBase
	from myshop.models.polymorphic.product import Product
	
	class ProductSummarySerializer(ProductSummarySerializerBase):
	    class Meta:
	        model = Product
	        fields = ('id', 'product_name', 'product_url',
	            'product_type', 'product_model', 'price')

All these fields can be extracted directly from the product model with the exception of the sample
image. This is because we yet do not know the final dimensions of the image inside its HTML element
such as ``<img src="...">``, and we certainly want to resize it using PIL/Pillow before it is
delivered. An easy way to solve this problem is to use the ``SerializerMethodField``. Simply extend
the above class to:

.. code-block:: python
	:linenos:

	from rest_framework.serializers import SerializerMethodField
	
	class ProductSummarySerializer(ProductSummarySerializerBase):
	    media = SerializerMethodField()
	
	    def get_media(self, product):
            return self.render_html(product, 'media')

As you might expect, ``render_html`` assigns a HTML snippet to the field ``media`` in the serialized
representation of our product. This method uses a template to render the HTML. The name of this
template is constructed using the following rules:

* Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` in lower
  case. If no such folder can be found, then use the folder named ``shop``.
* Search for a subfolder named ``products``.
* Search for a template named “*label*-*product_type*-*postfix*.html”. These three subfieds are
  determined using the following rule:
  * *label*: the component of the shop, for instance ``catalog``, ``cart``, ``order``.
  * *product_type*: the class name in lower case of the product's Django model, for instance
  ``smartcard``, ``smartphone`` or if no such template can be found, just  ``product``.
  * *postfix*: This is an arbitrary name passed in by the rendering function. As in the example
  above, this is the string ``media``.

.. note:: It might seem “un-restful” to render HTML snippets by a REST serializer and deliver them
	via JSON to the client. However, we somehow must re-size the images assigned to our product to
	fit into the layout of our list view. The easiest way to do this in a configurable manner is
	to use the easythumbnails_ library and its templatetag ``{% thumbnail product.sample_image ... %}``.

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


Serialize for the Product's Detail View
---------------------------------------

The serializer for the Product's Detail View is very similar to its List View serializer. In the
example as shown below, we even reverse the field listing by explicitly excluding the fields we're
not interested in, rather than naming the fields we want to include. This for the product's detail
view makes sense, since we want to expose every possible detail.

.. code-block:: python
	:linenos:

	from shop.rest.serializers import ProductDetailSerializerBase
	
	class ProductDetailSerializer(ProductDetailSerializerBase):
	    class Meta:
	        model = Product
	        exclude = ('active',)


.. _RESTful: https://en.wikipedia.org/wiki/Representational_state_transfer
.. _djangorestframework: http://www.django-rest-framework.org/
.. _easythumbnails: http://easy-thumbnails.readthedocs.org/


The ``AddToCartSerializer``
---------------------------

Rather than using the detail serializer, the business logic for adding a product to the cart has
been moved into a specialized serializer. This is because **djangoSHOP** can not presuppose that
products are added to the cart only from within the detail view[#add2cart]_. We also need a way to
add more than one product variant to the cart from each products detail page.

For this purpose **djangoSHOP** is shipped with an ``AddToCartSerializer``. It can be overridden
for special product requirements, but for a standard application it just should work out of the box.

Assure that the context for rendering a product contains the key ``product`` referring to the
product object. The ``ProductDetailSerializer`` does this by default. Then add

.. code-block:: django

	{% include "shop/catalog/product-add2cart.html" %}

to an appropriate location in the template which renders the product detail view.

The now included add-to-cart template contains a form with some input fields and a few AngularJS
directives, which communicate with the endpoint connected to the ``AddToCartSerializer``. It
updates the subtotal whenever the customer changes the quantity and displays a nice popup window,
whenever an item is added to the cart. Of course, that template can be extended with arbitrary HTML.

These Angular JS directives require some JavaScript code which is located in the file
``shop/js/catalog.js``; it is referenced automatically when using the above template include
statement.

.. [#add2cart] Specially in business-to-business sites, this usually is done in the list views.


Connect the Serializers with the View classes
=============================================

Now that we declared the serializers for the product's list- and detail view, the final step is to
access them through a CMS page. Remember, since we've chosen to use CMS pages as categories, we had
to set a special **djangoCMS** apphook_:

.. code-block:: python
	:caption: myshop/cms_app.py
	:linenos:

	from cms.app_base import CMSApp
	from cms.apphook_pool import apphook_pool
	
	class ProductsListApp(CMSApp):
	    name = _("Products List")
	    urls = ['myshop.urls.products']
	
	apphook_pool.register(ProductsListApp)

This apphook points onto a list of boilerplate code containing these urlpattern:

.. code-block:: python
	:caption: myshop/urls/products.py
	:linenos:

	from django.conf.urls import patterns, url
	from rest_framework.settings import api_settings
	from shop.rest.filters import CMSPagesFilterBackend
	from shop.rest.serializers import AddToCartSerializer
	from shop.views.catalog import (CMSPageProductListView,
	    ProductRetrieveView, AddToCartView)
	
	urlpatterns = patterns('',
	    url(r'^$', CMSPageProductListView.as_view(
	        serializer_class=ProductSummarySerializer,
	    )),
	    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(
	        serializer_class=ProductDetailSerializer
	    )),
	    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
	)

These URL patterns connect the product serializers with the catalog views in order to assign them
an endpoint. Additional note: The filter class ``CMSPagesFilterBackend`` is used to restrict
products to specific CMS pages, hence it can be regarded as the product categoriser.
