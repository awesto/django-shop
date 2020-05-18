.. _reference/catalog:

=======
Catalog
=======

The catalog presumably is that part, where customers of our e-commerce site spend most of their
time. Often it even makes sense, to start the :ref:`reference/catalog-list` on the main landing
page.

In this documentation we presume that categories of products are built up using specially tagged
**django-CMS** pages in combination with a `django-CMS apphook`_. This works perfectly well for most
implementations, but some sites may require categories implemented independently of the CMS.

Using an external **django-SHOP** plugin for managing categories is a very conceivable solution,
and we will see separate implementations for this feature request. Using such an external category
plugin can make sense, if an e-commerce site requires hundreds of hierarchical levels and/or
these category implementations can provide functionality, which is not available in **django-CMS**
pages. If you are going to use externally implemented categories, please refer to their
documentation, since in this document, we proceed using standard CMS pages as product categories.

It should be emphasized, that nowadays the classical hierarchy of categories is no longer
contemporary. Instead many merchants tag their products with different attributes. This provides a
better browsing experience, since customers usually filter by product characteristics, rather than
categories.

A nice aspect of **django-SHOP** is, that it doesn't require the programmer to write any special
Django Views in order to render the catalog. Instead all merchant dependent business logic goes
into a serializer, which in this documentation is referred as ``ProductSerializer``.


.. _reference/catalog-list:

Catalog List View
=================

In this documentation, the *Catalog List View* is implemented as a **django-CMS** page. Depending on
whether the e-commerce aspect of that site is the most prominent part or just a niche of the CMS,
select an appropriate location in the page tree and create a new page. This will become the root
of our catalog list.

.. note::
	If required, we can add as many catalog list views as we want, and distribute them accross the
	CMS page tree.

But first we must :ref:`reference/create-CatalogListApp`.


.. _reference/create-CatalogListApp:

Create the ``CatalogListApp``
-----------------------------

To retrieve a list of product models, the *Catalog List View* requires a `django-CMS apphook`_. For
this, we must inherit from :class:`shop.cms_apphooks.CatalogListCMSApp` and add that class
declaration to a file named ``cms_apps.py``, located in the root folder of our merchant's project:

.. code-block:: python
	:caption: myshop/cms_apps.py

	from cms.apphook_pool import apphook_pool
	from shop.cms_apphooks import CatalogListCMSApp
	from shop.rest.filters import CMSPagesFilterBackend

	class CatalogListApp(CatalogListCMSApp):
	    def get_urls(self, page=None, language=None, **kwargs):
	        from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView

	        filter_backends = [CMSPagesFilterBackend]
	        filter_backends.extend(api_settings.DEFAULT_FILTER_BACKENDS)
	        return [
	            url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
	            url(r'^(?P<slug>[\w-]+)', ProductRetrieveView.as_view()),
	            url(r'^', ProductListView.as_view(
	                filter_backends=filter_backends,
	            )),
	        ]

	apphook_pool.register(CatalogListApp)

In the page tree editor of **django-CMS**, we create a new page at an appropriate node. As the
page title and slug we should use something describing our product catalog in a way, both meaningful
to the customers as well as to search engines.

As template, select one with a placeholder large enough to display the figures of the catalog's
list .

Change into the **Advanced Settings** of the CMS page, which shall act as the catalog list. As
**Application**, select "*Catalog List*" from the drop-down menu. This selects the apphook
``CatalogListApp``, we just created.

.. note:: After adding or modifying a CMS apphook, we must restart the server.

Then we go into the page's **Preview** mode and open the **Structure menu** on the right side of the
**django-CMS** toolbar. Now locate the placeholder named **Main Content**. Add a Container plugin,
followed by a Row and then by a Column plugin. As the child of this column, choose the *Catalog List
View* plugin from section **Shop**.

Finally we publish the page, it probably doesn't contain any products yet. To fill it, we first have
to :ref:`reference/assign-products-to-cms-page`.

Remember to repeat this procedure, and add one CMS pages per category, in order to create a
structure of pages for our e-commerce site.


.. _reference/assign-products-to-cms-page:

Assign Products to CMS Pages
----------------------------

Here the :class:`shop.views.catalog.ProductListView` is configured to render the catalog list of
products assigned to one or more CMS pages. For this purpose we use the filter backend
:class:`shop.rest.filters.CMSPagesFilterBackend`. In order to decide to which CMS page a product is
assigned to, our product model must inherit from :class:`shop.models.product.CMSPageReferenceMixin`.
This is because we must add a reference to the CMS pages our products are assigned to. A typical
product might be declared as:

.. code-block:: python

	from shop.models.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin

	class MyProduct(CMSPageReferenceMixin, BaseProduct):
	    product_name = models.CharField(
	        _("Product Name"),
	        max_length=255,
	    )

	    slug = models.SlugField(
	        _("Slug"),
	        unique=True,
	    )

	    # other fields making up our product

	    cms_pages = models.ManyToManyField(
	        'cms.Page',
	        through=ProductPage,
	        help_text="Choose page this product shall appear on.",
	    )

	    objects = BaseProductManager()

An important part of this product model is the field ``cms_pages = ManyToManyField(...)``.
Mapping a relationship between CMS pages and products, the merchant can emulate categories by
assigning a product to one ore more CMS pages. Products added to those CMS pages, then shall be
visible in the *Catalog List View* plugin.

As we work with deferred models, we can not use the mapping table, which normally is generated
automatically for many-to-many fields by the Django framework. Instead, we must refer to the
mapping table :class:`shop.models.defaults.mapping.ProductPage` explicitely, using the ``though``
parameter, when declaring the field ``cms_pages``.


.. _reference/product-summary-serializer:

Product Summary Serializer
--------------------------

In order to render the list view, we need to identify the fields common to all offered products.
This is because when rendering a list view, we usually want do have a consistent representation for
all products in our catalog. Since this catalog list can be rendered either by the server using the
class :class:`shop.rest.renderers.CMSPageRenderer`, or by the client using the AngularJS directive
``shop-catalog-list``, we must provide some functionality to serialize a summary representation for
all the products we want to list. This separation is important, so that we can reuse the view class
:class:`shop.views.catalog.ProductListView`, whenever we switch from the server-side rendered
catalog list into infinite scroll mode, which for technical reasons can only be rendered by the
client.

For this purpose, we have to declare a product summary serializer using the configuration directive
``SHOP_PRODUCT_SUMMARY_SERIALIZER``. Remember that **django-SHOP** does not impose which fields a
product must offer, it's up to the merchant to declare this product summary serializer as well.
A typical implementation might look like:

.. code-block:: python

	class ProductSummarySerializer(ProductSerializer):
	    media = serializers.SerializerMethodField(
	        help_text="Returns a rendered HTML snippet containing a sample image among other elements",
	    )

	    class Meta(ProductSerializer.Meta):
	        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media']

	    def get_media(self, product):
	        return self.render_html(product, 'media')

Here we assume that our product models have a very limited set of common fields. They may for
instance have a field to store a caption text and an image. Those two fields then can be rendered
into a HTML snippet, which here we name ``media``. Using method
:meth:`shop.serializers.bases.ProductSerializer.render_html()`, this snipped is rendered by the
serializer itself, looking for a Django template following these rules:

* look for a template named :samp:`{app_label}/products/catalog-{product-model-name}-{field-name}.html`
  [#app_label]_ [#product-model-name]_ [#field-name]_, otherwise
* look for a template named :samp:`{app_label}/products/catalog-product-{field-name}.html``
  [#app_label]_ [#field-name]_,
  otherwise
* use the template ``shop/product/catalog-product-media.html``.

.. [#app_label] :samp:`{app_label}` is the app label of the project in lowercase.
.. [#product-model-name] :samp:`{product-model-name}` is the class name of the product model in lowercase.
.. [#field-name] :samp:`{field-name}` can be any lowercased identifier, but by convenience shall be the name
       of the serializer field. In this example we use ``media`` as field name.

.. note::
	When rendering images, we have to create a thumbnailed version and put its URL into a
	``<img src="..." />`` tag. This means that we then have to know the thumbnailed size of the
	final image, so that the templatetag `thumb`_ from the easythumbnail library knows what to do.
	Otherwise we would have to refer to the original, often much heavier image and thumbnail it
	on the fly, which would be pretty inefficient.

To test if that serializer works properly, we can examine the raw content of the declared fields by
appending ``?format=api`` to the URL of our catalog view. This then renders a human readable
representation of the context as JSON.

.. _thumb: https://easy-thumbnails.readthedocs.io/en/latest/usage/#thumbnail-tag


.. _reference/customized-product-serializer:

Customizing the Product Summary Serializer
..........................................

In case we need serialized content from other fields of our product model, let's add them to a
customized product serializer class: For this we use the `serializer fields`_ from the Django's
RESTFramework library. This can be useful for product serializers, which shall provide additional
information on our catalog list view. If we have to map fields from our product model, just add
them to the list of fields in the ``Meta``-class. For example as:

.. code-block:: python

	from shop.serializers.bases import ProductSerializer

	class CustomizedProductSerializer(ProductSerializer):
	    class Meta:
	        model = CustomProductModel
	        fields = [all-the-fields-required-for-the-list-view]

Additionally, we have to rewrite the apphook from above as:

.. code-block:: python

	class CatalogListApp(CatalogListCMSApp):
	    def get_urls(self, page=None, language=None, **kwargs):
	        ...

	        return [
	            ...
	            url(r'^', ProductListView.as_view(
	                filter_backends=...,
	                serializer_class=CustomizedProductSerializer,
	            )),
	        ]

By specifiying an alternative product sumary serializer, we can create a more specialized
representation of our product models.

A nice aspect of this is, that we can create one apphook per product model. This can be useful, if
we want to render a different kind of catalog list per product type. Say, our shop offers two
product models, ``Book`` and ``Magazine`` and both of these models have their own list serializers.
Then by restricting our ``ProductListView`` to one product model using its customized serializer,
we can build two different list views, one for books and one for magazines. If we want to restrict
our list view to magazines only, we simply pass ``limit_choices_to = Q(instance_of=Book)`` to the
above ``as_view()``-method.


.. _reference/catalog-detail:

Catalog Detail View
===================

The apphook ``CatalogListApp`` as show above, is also responsible for routing to the product's
detail view. This is why our product declares a ``SlugField``. The product's slug then is appended
to the URL of the CMS page, also referred as category. This approach generates nicely spelled URLs.

A product detail view is rendered by the :class:`shop.views.catalog.ProductRetrieveView` and is
*not* managed by **django-CMS**. Instead, this product detail view behaves like a normal Django
view, with its own context objects and rendered by a specifc template. This is because we often
have thousands of different products and creating one CMS page for each of them, would be a far
bigger effort, rather than handcrafting a specific template for each product type.

When rendering a product's detail page, the ``ProductRetrieveView`` looks for a template suitable
for the given product type, following these rules:

* look for a template named :samp:`{app_label}>/catalog/{product-model-name}-detail.html` [4]_ [5]_,
  otherwise
* look for a template named :samp:`{app_label}/catalog/product-detail.html` [4]_, otherwise
* use the template samp:`shop/catalog/product-detail.html`.

This means that the template to render the products's detail view is selected automatically by the
:class:`shop.views.catalog.ProductRetrieveView`. When rendered as HTML, this view adds the product
model to the context, so that the rendering templates can refer to this context variable.

.. [4] *app_label* is the app label of the project in lowercase.
.. [5] *product-model-name* is the class name of the product model in lowercase.


Use CMS Placeholders in the Detail View
---------------------------------------

Sometime we want to add any kind of **django-CMS** plugins to our product's detail pages. To achieve
this, we need to add a `django-CMS Placeholder field`_ named ``placeholder``, to the class
implementing our product model. Then we add the templatetag
``{% render_placeholder product.placeholder %}`` to the template implementing the detail view of
that product. Now this placeholder can be used to add any arbitrary content to the product's detail
page. This for instance can be a CMS plugin to add text paragraphs, additional images, a carousel,
a video, or whatever else is available from the **django-CMS** plugin system.

.. note::
	The built-in product model :class:`shop.models.defaults.commodity.Commodity` makes heavy
	use of that placeholder field. The commodity model actually doesn't offer any other fields,
	other than the product's code, its name and price. So all relevant information must be added to
	the product's detail view using the **django-CMS** structure editor.


Customizing the Product Detail Serializer
-----------------------------------------

If we need additional business logic regarding our product, we can create a customized serializer
class, named for instance ``CustomizedProductDetailSerializer``. This class then may access the
various attributes of our product model, recombine them and/or merge them into a serializable
representation, as described in :ref:`reference/customized-product-serializer`.

Additionally, we have to rewrite the apphook from above as:

.. code-block:: python

	class CatalogListApp(CatalogListCMSApp):
	    def get_urls(self, page=None, language=None, **kwargs):
	        ...

	        return [
	            ...
	            url(r'^', ProductRetrieveView.as_view(
	                serializer_class=CustomProductDetailSerializer,
	            )),
	        ]


Add Product to Cart
===================

By looking at the URL routings above, the savvy reader may have noticed, that for each product's
detail view, there is an extra endpoint ending in ``.../add-to-cart``. Its URL points onto the class
:class:`shop.views.catalog.AddToCartView`. This view handles the communication between the control
form for adding the given product to the cart on the client, and the REST endpoints on the server.

Each product's detail page shall implement a HTML element containing the AngularJS directive
``shop-add-to-cart``. This directive fetches the availability, price and cart status, and fills out
the "add to cart" form. If the customer submits that form data, the item is added either to the
cart, or the watch-list.

To help integration, **django-SHOP** offers a HTML snippet for this purpose. It can be included as
``shop/templates/shop/catalog/product-add2cart.html`` or, if we must handle the current availability
``shop/templates/shop/catalog/available-product-add2cart.html``. It's up to the merchant to use and
extend these templates to fit the representation for his own products.

For products with a **django-CMS** placeholder field, the merchant can also use the plugin named
"*Add Product to Cart*". This plugin then shall be added into the structure of the product's detail
page. Products of type "Commodity" make use of this plugin.


Products with variations
------------------------

In some situations, it might be neccessary to use a custom endpoint for adding a product to the
cart. This for instance is required, when the product to be added contains variations. We then
rewrite our ``CatalogListApp`` to use this url pattern:

.. code-block:: python

	class CatalogListApp(CatalogListCMSApp):
	    def get_urls(self, page=None, language=None, **kwargs):
	        ...
	        return [
	            ...
	            url(r'^(?P<slug>[\w-]+)/add-product-to-cart', AddToCartView.as_view(
	                serializer_class=AddProductWithVariationsSerializer,
	            )),
	            ...
	        ]

We then create a special serializer for that view:

.. code-block:: python

	from shop.models.cart import CartModel
	from shop.serializers.defaults.catalog import AddToCartSerializer

	class AddProductWithVariationsSerializer(AddToCartSerializer):
	    def get_instance(self, context, data, extra_args):
	        product = context['product']
	        cart = CartModel.objects.get_from_request(context['request'])
	        variant = product.get_product_variant(product_code=data['product_code'])
	        is_in_cart = bool(product.is_in_cart(cart, product_code=variant.product_code))
	        instance = {
	            'product': product.id,
	            'product_code': variant.product_code,
	            'unit_price': variant.unit_price,
	            'is_in_cart': is_in_cart,
	        }
	        return instance

This serializer is adopted to a product with variations. Each variation of the product provides
its own product code and a price. Additionally we want to know, whether the same variation of
that product is already in the cart (increasing the quantity), or if it has to be considered as
different product (adding a new one to the cart). For indicating this state, the serializer returns
a flag, named ``is_in_cart``.


Admin Integration
=================

To simplify the declaration of the admin backend used to manage our Product model, **django-SHOP**
is shipped with a special mixin class, which shall be added to the product's admin class:

.. code-block:: python

	from django.contrib import admin
	from shop.admin.product import CMSPageAsCategoryMixin
	from myshop.models import Product

	@admin.register(Product)
	class ProductAdmin(CMSPageAsCategoryMixin, admin.ModelAdmin):
	    fields = [
	        'product_name', 'slug', 'product_code',
	        'unit_price', 'active', 'description',
	        # other model fields
	    ]
	    # other admin declarations

This then adds a horizontal filter widget to the product models. Here the merchant must select
each CMS page, where the currently edited product shall appear on.

If caching is configured and enabled, HTML snippets rendered by the method ``render_html()`` are
cached by **django-SHOP**. Caching these snippets is highly recommended and gives a noticeable
performance boost, specially while rendering catalog list views.

Since we would have to wait until they expire naturally by reaching their expire time,
**django-SHOP** offers the mixin class :class:`shop.admin.product.InvalidateProductCacheMixin`. This
should be added to the ``ProductAdmin`` class. It then expires all HTML snippets of a product,
whenever a product in saved by the backend.

.. note:: Due to the way keys are handled in many caching systems, the ``InvalidateProductCacheMixin``
	only makes sense if used in combination with the redis_cache_ backend.

.. _django-CMS apphook: http://docs.django-cms.org/en/stable/how_to/apphooks.html
.. _django-CMS Placeholder field: http://django-cms.readthedocs.org/en/stable/how_to/placeholders.html
.. _serializer fields: http://www.django-rest-framework.org/api-guide/fields/
.. _templatetags from the easythumbnail: https://easy-thumbnails.readthedocs.org/en/stable/usage/#templates
.. _redis_cache: http://django-redis-cache.readthedocs.org/en/stable/
