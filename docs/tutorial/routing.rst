==================
Routes to Products
==================

Now that we know how to create product models and how to administer them, lets have a look on how
to route them to our views. A nice aspect of **djangoSHOP** is, that it doesn't require the
programmer to write any special Django Views to render the products to be sold. Instead all
business logic shall go into their model classes, their model managers or into their serializers.


Product List Views
==================

Although in **djangoSHOP** it is possible to create explicit list views for products, even a simple
CMS page can used in combination with an apphook_.

When editing the CMS page used for the products list view, open **Advanced Settings** and chose
**Products List** from the select box labeled **Application**.

Use a template with at least one placeholder_. Click onto **View on site** to change into front-end
editing mode. Locate your main placeholder and add a **Row** followed by a **Column** plugin from
the section **Bootstrap**. Below that column add a **Catalog List Views** plugin from section
**Shop**. Then publish the page, it should not display any products yet.

.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html
.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders


Add products to the category
----------------------------

Open the detail view of a product in Django's administration backend. Locate the many-to-many
select box labeled **Categories > Cms pages**. Select the pages where each product shall appear
on.

On reloading the list view, the assigned products now shall be visible. Assure that they have been
set to be active.

If you nest categories, products assigned to children will be also be visible on their parents.


Product Model Serializers
=========================

We already learned how to write model classes and model managers, so what are serializers for?
In **djangoSHOP** the response views do not distinguish whether the product's information shall
be rendered as HTML or transferred via JSON. This gives us the ability to use the same business
logic for web browsers as well as for native shopping applications. This is one of the great
benefits when working with RESTful_ API's and thanks to the djangorestframework_ we don't even
have to write any Django Views anymore.

For instance, try to open the list- or the detail view of any of the products available in the
shop. Then in the browser append ``?format=api`` or ``?format=json`` to the URL. This will render
the pure product information, but without embedding it into HTML.

The REST API view is very handy while developing. If you want to hide this on your production
system , then in your settingy.py remove ``'rest_framework.renderers.BrowsableAPIRenderer'`` from 
``REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']``.

In the shop's catalog, we need some functionality to render a list view for all products and
we need a detail view to render each product type. The **djangoSHOP** framework supplies two
such serializers:


Serialize for the Product's List View
-------------------------------------

For each product we want to display in a list view, we need a serializer which converts the content
of the most important fields of a product. Normally these are the Id, the name and price, the URL
onto the detail view, a short description and a sample image.

.. code-block:: python
	:linenos:

	from shop.rest.serializers import ProductSummarySerializerBase
	from myshop.models.polymorphic.product import Product
	
	class ProductSummarySerializer(ProductSummarySerializerBase):
	    class Meta:
	        model = Product
	        fields = ('id', 'product_name', 'product_url',
	            'product_type', 'product_model', 'price')

All these fields can be extracted directly from the product model with the exception of the sample
image. This is because we yet do not know the final dimensions of the image inside its HTML tag
``<img src="...">``. An easy way to solve this problem is to use the ``SerializerMethodField``. Just
extend the above class to:

.. code-block:: python
	:linenos:

	from rest_framework.serializers import SerializerMethodField
	
	class ProductSummarySerializer(ProductSummarySerializerBase):
	    media = SerializerMethodField()
	
	    def get_media(self, product):
            return self.render_html(product, 'media')

As you might expect, ``render_html`` assigns a HTML snippet to the field ``media`` in the serialized
representation of our product. This method uses a template to render the HTML. The name of this
template is constructed using these rules:

* Look for a folder named according to the project's name, ie. ``settings.SHOP_APP_LABEL`` lower
  case. If no such folder could be found, use the name ``shop``.
* Search for a subfolder named ``products``.
* Search for a template named “*label*-*product_type*-*postfix*.html”. These three subfieds are
  determined using these rules:
 * *label*: the component of the shop, for instance ``catalog``, ``cart``, ``order``.
 * *product_type*: the class name in lower case of the product's Django model, for instance
   ``smartcard``, ``smartphone`` or if no such template can be found, just  ``product``.
 * *postfix*: This is an arbitrary name passed in by the rendering function. As in the example
   above, this is the string ``media``.

.. note:: It might seem “un-restful” to render HTML snippets by a REST serializer and deliver them
	via JSON to the client. However, we somehow must re-size the images assigned to our product to
	fit into the layout of our list view. The easiest way to do this in a configurable manner is
	to use the easythumbnails_ library and its templatetag ``{% thumbnail product.sample_image ... %}``.


Serialize for the Product's Detail View
---------------------------------------

The serializer for the Product's Detail View is quite similar. In the example as shown below, we
even reverse the field listing by explicitly excluding the fields we're not interested in, rather
than naming the fields to include. This for the product's detail view makes sense, since we want
to expose every possible detail.

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
products are added to the cart only from within the detail view. Specially in business-to-business
sites, this usually is done in the list views.

For this purpose **djangoSHOP** is shipped with an ``AddToCartSerializer``. It can be overridden
for special product requirements, but for a standard application it just should work out of the box.

Assure that the context for rendering a product contains the key ``product`` referring to the
product object. The ``ProductDetailSerializer`` does this by default. Then add

.. code-block:: django

	{% include "shop/catalog/product-add2cart.html" %}

to an appropriate location in the template which renders the product details.

This included add-to-cart template contains a form with some input fields and a few AngularJS
directives, which communicate with the endpoint connected to the ``AddToCartSerializer``. It
updates the subtotal whenever the customer changes the quantity and displays a nice popup window,
whenever an item is added to the cart. Of course, that template can be extended with arbitrary HTML.


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

This apphook requires some urlpatterns as:

.. code-block:: python
	:caption: myshop/urls/products.py
	:linenos:

	from django.conf.urls import patterns, url
	from rest_framework.settings import api_settings
	from shop.rest.filters import CMSPagesFilterBackend
	from shop.rest.serializers import AddToCartSerializer
	from shop.views.product import (AddToCartView,
	    ProductListView, ProductRetrieveView)
	
	list_options = dict(
	    serializer_class=ProductSummarySerializer,
	    filter_backends=api_settings.DEFAULT_FILTER_BACKENDS \
	        + [CMSPagesFilterBackend()],
	)
	detail_options = dict(
	    serializer_class=ProductDetailSerializer,
	    lookup_field='slug',
	)
	add2cart_options = dict(
	    serializer_class=AddToCartSerializer,
	    lookup_field='slug',
	)
	
	urlpatterns = patterns('',
	    url(r'^$', ProductListView.as_view(**list_options)),
	    url(r'^(?P<slug>[\w-]+)$',
	        ProductRetrieveView.as_view(**detail_options)),
	    url(r'^(?P<slug>[\w-]+)/add-to-cart',
	        AddToCartView.as_view(**add2cart_options)),
	)
