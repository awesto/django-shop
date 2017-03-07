.. _reference/catalog:

=======
Catalog
=======

The catalog presumably is that part, where customers of our e-commerce site spend the most time.
Often it even makes sense, to start the :ref:`reference/catalog-list` on the main landing page.

In this documentation we presume that categories of products are built up using specially tagged
CMS pages in combination with a `djangoCMS apphook`_. This works perfectly well for most
implementation, but some sites may require categories implemented independently of the CMS.

Using an external **django-SHOP** plugin for managing categories is a very conceivable solution,
and we will see separate implementations for this feature request. Using such an external category
plugin can make sense, if this e-commerce site requires hundreds of hierarchical levels and/or
these categories require a set of attributes which are not available in CMS pages. If you are
going to use externally implemented categories, please refer to their documentation, since here we
proceed using CMS pages as categories.

A nice aspect of **django-SHOP** is, that it doesn't require the programmer to write any special
Django Views in order to render the catalog. Instead all merchant dependent business logic goes
into a serializer, which in this documentation is referred as ``ProductSerializer``.


.. _reference/catalog-list:

Catalog List View
=================

In this documentation, the catalog list view is implemented as a **django-CMS** page. Depending on
whether the e-commerce aspect of that site is the most prominent part or just a niche of the CMS,
select an appropriate location in the page tree and create a new page. This will become the root
of our catalog list.

But first we must :ref:`reference/create-ProductsListApp`.


.. _reference/create-ProductsListApp:

Create the ``ProductsListApp``
------------------------------

To retrieve a list of product models, the Catalog List View requires a `djangoCMS apphook`_. This
``ProductsListApp`` must be added into a file named ``cms_apps.py`` and located in the root folder
of the merchant's project:

.. code-block:: python
	:caption: myshop/cms_apps.py

	from cms.app_base import CMSApp
	from cms.apphook_pool import apphook_pool

	class ProductsListApp(CMSApp):
	    name = _("Catalog List")
	    urls = ['myshop.urls.products']

	apphook_pool.register(ProductsListApp)

as all apphooks, it requires a file defining its urlpatterns:

.. code-block:: python
    :caption: myshop/urls/products.py
    :name: apphook-urlpatterns

	from django.conf.urls import url
	from rest_framework.settings import api_settings
	from shop.views.catalog import CMSPageProductListView

	urlpatterns = [
	    url(r'^$', CMSPageProductListView.as_view()),
	    # other patterns
	]

By default the ``CMSPageProductListView`` renders the catalog list of products assigned to the
current CMS page. In this example, only model attributes for fields declared in the default
``ProductSummarySerializer`` are available in the render context for the used CMS template, as well
as for a representation in JSON suitable for client side rendered list views. This allows us to
reuse the same Django View (``CMSPageProductListView``) whenever the catalog list switches into
infinite scroll mode, where it only requires the product's summary, composed of plain old JavaScript
objects.


.. _reference/customized-product-serializer:

Customized Product Serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case we need :ref:`reference/additional-serializer-fields`, let's add them to this class using
the `serializer fields`_ from the Django RESTFramework library. This can be useful for product
serializers which shall provide more information on our catalog list view.

For this customized serializer, we normally only require a few attributes from our model, therefore
we can write it as:

.. code-block:: python

	from shop.serializers.bases import ProductSerializer

	class CustomizedProductSerializer(ProductSerializer):
	    class Meta:
	        model = Product
	        fields = [all-the-fields-required-for-the-list-view]

Additionally, we have to rewrite the URL pattern from above as:

.. code-block:: python

	from myshop.serializers import CustomizedProductSerializer

	urlpatterns = [
	    url(CMSPageProductListView.as_view(
	        serializer_class=CustomizedProductSerializer,
	    )),
	    # other patterns
	]

Here the ``CustomizedProductSerializer`` is a more specialized representation of our product
model.


Add the Catalog to the CMS
--------------------------

In the page list editor of **djangoCMS**, create a new page at an appropriate location of the
page tree. As the page title and slug we should use something describing our product catalog in a
way, both meaningful to the customers as well as to search engines.

Next, we change into **Advanced Settings** mode.

As a template we use one with a big placeholder, since it must display our list of products.

As **Application**, select "*Catalog List*" or whatever we named our ``ProductsListApp``. This
selects the apphook we created in the previous section.

Then we save the page, change into **Structure** mode and locate the placeholder named
**Main Content**. Add a Container plugin, followed by a Row and then a Column plugin. As the
child of this column choose the **Catalog List View** plugin from section **Shop**.

Finally we publish the page. If we have assigned products to that CMS page, they should be rendered
now.


.. _reference/catalog-detail:

Catalog Detail View
===================

The product's detail pages are the only ones we typically do not control with **djangoCMS**
placeholders. This is because we often have thousands of products and creating a CMS page for each
of them, would be kind of overkill. It only makes sense for shops selling up to a dozen of different
products.

Therefore the template used to render the products's detail view is selected automatically by the
``ProductRetrieveView`` [1]_ following these rules:

* look for a template named ``<myshop>/catalog/<product-model-name>-detail.html`` [2]_ [3]_,
  otherwise
* look for a template named ``<myshop>/catalog/product-detail.html`` [2]_, otherwise
* use the template ``shop/catalog/product-detail.html``.

.. [1] This is the View class responsible for rendering the product's detail view.
.. [2] ``<myshop>`` is the app label of the project in lowercase.
.. [3] ``<product-model-name>`` is the class name of the product model in lowercase.


Use CMS Placeholders on Detail View
-----------------------------------

If we require CMS functionality for each product's detail page, its quite simple to achieve. To the
class implementing our product model, add a `djangoCMS Placeholder field`_ named ``placeholder``.
Then add the templatetag ``{% render_placeholder product.placeholder %}`` to the template
implementing the detail view of our product. This placeholder then shall be used to add arbitrary
content to the product's detail page. This for instance can be an additional text paragraphs,
some images, a carousel or whatever is available from the **djangoCMS** plugin system.


Route requests on Detail View
-----------------------------

The ``ProductsListApp``, which we previously have registered into **djangoCMS**, is able to route
requests on all of its sub-URLs. This is done by expanding the current list of urlpatterns:

.. code-block:: python
    :caption: myshop/urls/products.py
    :name: productlist-urlpatterns

	from django.conf.urls import url
	from shop.views.catalog import ProductRetrieveView

	urlpatterns = [
	    # previous patterns
	    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view()),
	    # more patterns
	]

If we need additional business logic regarding our product, we can create a customized serializer
class, named for instance ``CustomizedProductDetailSerializer``. This class then may access the
various attributes of our product model, recombine them and/or merge them into a serializable
representation, as described in :ref:`reference/customized-product-serializer`.

Additionally, we have to rewrite the URL pattern from above as:

.. code-block:: python

	from myshop.serializers import CustomizedProductDetailSerializer

	urlpatterns = [
	    # previous patterns
	    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(
	        serializer_class=CustomizedProductDetailSerializer,
	    )),
	    # more patterns
	]


.. _reference/additional-serializer-fields:

Additional Product Serializer Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes such a serializer field shall return a HTML snippet; this for instance is required for
image source (``<img src="..." />``) tags, which must thumbnailed by the server when rendered using
the appropriate `templatetags from the easythumbnail`_ library. For these use cases add a field
of type ``foo = SerializerMethodField()`` with an appropriate method ``get_foo()`` to our serializer
class. This method then may forward the given product to a the built-in renderer:

.. code-block:: python

	class ProductDetailSerializer(BaseProductDetailSerializer):
	    # other attributes

	    def get_foo(self, product):
	        return self.render_html(product, 'foo')

This HTML renderer method looks up for a template following these rules:

* look for a template named ``<myshop>/product/catalog-<product-model-name>-<second-argument>.html``
  [4]_ [5]_ [6]_, otherwise
* look for a template named ``<myshop>/product/catalog-product-<second-argument>.html`` [4]_ [6]_,
  otherwise
* use the template ``shop/product/catalog-product-<second-argument>.html`` [6]_.

.. [4] ``<myshop>`` is the app label of the project in lowercase.
.. [5] ``<product-model-name>`` is the class name of the product model in lowercase.
.. [6] ``<field-name>`` is the attribute name of the just declared field in lowercase.

Emulate Categories
------------------

Since we want to use CMS pages to emulate categories, the product model must declare a relationship
between the CMS pages and itself. This usually is done by adding a Many-to-Many field named
``cms_pages`` to our Product model.

Since we work with deferred models, we can not use the mapping table, which normally is generated
automatically for Many-to-Many fields by the Django framework. Instead, this mapping table must
be created manually and referenced using the ``though`` parameter, when declaring the field:

.. code-block:: python

	from shop.models.product import BaseProductManager, BaseProduct
	from shop.models.related import BaseProductPage

	class ProductPage(BaseProductPage):
	    """Materialize many-to-many relation with CMS pages"""

	class Product(BaseProduct):
	    # other model fields
	    cms_pages = models.ManyToManyField('cms.Page',
	        through=ProductPage)

	    objects = ProductManager()

In this example the class ``ProductPage`` is responsible for storing the mapping information
between our Product objects and the CMS pages.


Admin Integration
~~~~~~~~~~~~~~~~~

To simplify the declaration of the admin backend used to manage our Product model, **django-SHOP**
is shipped with a special mixin class, which shall be added to the product's admin class:

.. code-block:: python

	from django.contrib import admin
	from shop.admin.product import CMSPageAsCategoryMixin
	from myshop.models import Product

	@admin.register(Product)
	class ProductAdmin(CMSPageAsCategoryMixin, admin.ModelAdmin):
	    fields = ('product_name', 'slug', 'product_code',
	              'unit_price', 'active', 'description',)
	    # other admin declarations

This then adds a horizontal filter widget to the product models. Here the merchant must select
each CMS page, where the currently edited product shall appear on.

If we are using the method ``render_html()`` to render HTML snippets, these are cached by
**django-SHOP**, if caching is configured and enabled for that project. Caching these snippets is
highly recommended and gives a noticeable performance boost, specially while rendering catalog list
views.

Since we would have to wait until they expire naturally by reaching their expire time,
**django-SHOP** offers a mixin class to be added to the Product admin class, to expire all HTML
snippets of a product altogether, whenever a product in saved in the backend. Simply add
:class:`shop.admin.product.InvalidateProductCacheMixin` to the ``ProductAdmin`` class described
above.

.. note:: Due to the way keys are handled in many caching systems, the ``InvalidateProductCacheMixin``
	only makes sense if used in combination with the redis_cache_ backend.

.. _djangoCMS apphook: http://docs.django-cms.org/en/stable/how_to/apphooks.html
.. _djangoCMS Placeholder field: http://django-cms.readthedocs.org/en/stable/how_to/placeholders.html
.. _serializer fields: http://www.django-rest-framework.org/api-guide/fields/
.. _templatetags from the easythumbnail: https://easy-thumbnails.readthedocs.org/en/stable/usage/#templates
.. _redis_cache: http://django-redis-cache.readthedocs.org/en/stable/
