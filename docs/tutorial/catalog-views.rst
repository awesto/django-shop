.. _tutorial/catalog-views:

=============
Catalog Views
=============

In **django-SHOP**, every URL, which points to a page visible by the customer, is managed by the
CMS. This means that we are completely free, in how we organize the structure of our page-tree.
There are however a few things to consider, when building a working e-commerce site.

The catalog page(s) is where we present the products, we want to sell. In a shop, we can add as
many catalog pages to the CMS, but there should be at least one, even if the shop only sells
one product exclusively.

When editing the CMS page used for the products list view, open **Advanced Settings** and choose
**Products List** from the select box labeled **Application**.

Then choose a template with at least one placeholder_. Click onto **View on site** to change into
front-end editing mode. Locate the main placeholder of the template, and from section **Bootstrap**,
add a **Container**-plugin, followed by a **Row**-, followed by a **Column**-plugin. Below that
column add a **Catalog List Views**-plugin from section **Shop**. Then publish the page, it should
not display any products yet.

**Django-SHOP** does not distinguish between categories and a catalog pages. If our shop needs a
hierarchy of different categories, we organize them using many catalog pages nested into each other.
Each product can be assigned to as many catalog pages as we want.

.. _placeholder: http://django-cms.readthedocs.org/en/latest/introduction/templates_placeholders.html#placeholders


Assign products to their category
=================================

In Django's administration backend, find the list view for products. Depending on the name of a
given product type, this can be **Home › My Shop › Commodities**, **Home › My Shop › Products**, or
similar. Choose an item of that list to open the product's detail editor. Locate the many-to-many
select box labeled **Categories > Cms pages**. Select one or more CMS pages where the given product
shall appear on.

On reloading the catalog page, the assigned products shall now be visible in their list view.
Assure that they have been set to be active, otherwise they won't show up.

If we nest categories, products assigned to children will be also be visible on their parents
pages.


Configure Pagination
--------------------

The serializer used to create the list of products for the catalog's view, usually only renders a
subset, adding links pointing to other URLs for fetching neighboring subsets of that list. We also
name this "pagination". The component rendering the catalog's list view offers three different types
of pagination:

* Adding a paginator, where the customer can choose the neighboring page manually.
* Adding a simple paginator button, where by clicking one can extend the existing list of products.
* An automatic paginator, which triggers the extension of catalog's list, whenever the customer
  scrolls to the end of the page. We name this infinite scroll.

.. note:: If manual pagination is selected, **django-SHOP** tries to prevent widows – these are
	single items spawning over the last row. Say that the grid of the list can show 5✕3 items,
	then the 16nth item is hidden. If however we want to render 4✕4 items, then it is visible.
	A side-effect of this feature is, that the 16nth item is rendered again on the following page.


.. _tutorial/product-detail-view:

Product Detail Views
====================

In **django-SHOP's** frontend, each product can be rendered using their own detail view. However, we
neither have to, nor can't create a CMS page for each product. This is, because we have to store the
properties of a product, such as a unit price, product code, availability, etc. inside a Django
model. It furthermore would be tedious to create one CMS page per product, to render its detail
view. Therefore, products have to be assigned to their categories, rather than being children of
thereof.

This approach allows us to use CMS pages tagged as *Catalog List*, as product categories.
Furthermore, we can assign a product to more than one such category.

As with regular Django views, the product detail view is rendered by adding the product to the
context, and using a Django template to render HTML. If the product has custom properties, they
shall be referred by that template.

In the merchant implementation, each product type can provide their own template referring exactly
the properties of that model. On rendering, **django-SHOP** converts the classname of a product to
lowercase. Say, we want to render the detail view of an instance of our class ``SmartCard``. Then
we look for a template named

#. ``myshop/catalog/smartcard-detail.html``
#. if not found, then ``myshop/catalog/product-detail.html``
#. if not found, then ``shop/catalog/product-detail.html``

Inside this template we refer the properties as usual, for instance

.. code-block:: django

	<ul class="list-group">
	  <li class="list-group-item">
	    <div class="w-50">Product Code:</div>
	    <strong>{{ product.product_code }}</strong>
	  </li>
	  <li …
	</ul>

**Django-CMS** offers a useful templatetag to access the product backend editor, while navigating
on the product's detail view. The following HTML snippet renders the product title

.. code-block:: django

	{% load cms_tags %}
	<h1>{% render_model product "product_name" %}</h1>

with the possibility, that authenticated staff users may double click onto the title. In case the
CMS is in edit mode, the product's backend editor pops up and, allowing front-end editong by its
users.


Product Model Serializers
=========================

We already learned how to write model classes and model managers, so what are serializers for?

In **django-SHOP** the response views do not distinguish whether the product's information shall
be rendered as HTML or transferred via JSON. This gives us the ability to use the same business
logic for web browsers rendering static HTML, single page web applications communicating via AJAX
or native shopping applications for your mobile devices. This btw. is one of the great benefits
when working with RESTful_ API's and thanks to the djangorestframework_ we don't even have to
write any Django Views anymore.

Let's recap the shop's catalog list view. There we need some functionality to render a list of all
products and we need a detail view to render each product type. The **django-SHOP** framework
supplies two such serializers:

.. _RESTful: https://en.wikipedia.org/wiki/Representational_state_transfer
.. _djangorestframework: http://www.django-rest-framework.org/


Serialize the Products for the List View
----------------------------------------

For each product we want to display in a list view, we need a serializer which converts the content
of the most important fields of a product. Normally these are the Id, the product name, the URL
(onto the detail view), the product type, the price, a caption (short description) and some media
field to render a sample image.

For this purpose, the **django-SHOP** framework provides a default serializer,
:class:`shop.serializers.default.product_summary.ProductSummarySerializer`, which handles the most
common use cases. If required, it can be replaced by a customized implementation. Such a serializer
can be configured using a settings variable.

During development, it can be useful to examine what data this serializer delivers. In
**django-SHOP** the easiest way to achieve this, is to append ``?format=api`` to the URL on the
catalog's list view. This will show the context data to render the catalog, but without embedding
it into HTML.


Serializer for the Product's Detail View
----------------------------------------

The serializer for the Product's Detail View is very similar to its counterpart, the just described
``ProductSummarySerializer``. By default, the **django-SHOP** framework uses the serializer
:class:`shop.serializers.bases.ProductSerializer`. This serializer converts all properties of the
product model into a serialized representation. Of course, this serializer can also be replaced by
a custom implementation. Such a serializer can be configured by adopting the Detail View class, and
is explained in the programmers reference.

During development, it can be useful to examine what data this serializer delivers. The easiest way
to achieve this, is to append ``?format=api`` to the URL on the product's detail view. This will
show the context data to render the product detail view, but without embedding it into HTML.


The ``AddToCartSerializer``
---------------------------

Rather than using the detail serializer, the business logic for adding a product to the cart has
been moved into a specialized serializer. This is because in **django-SHOP** products can either
be added to the cart from within the detail view [#add2cart]_, or from their catalog list view.
We also need a way to add more than one product variant to the cart from each products detail page.

For this purpose **django-SHOP** is shipped with an ``AddToCartSerializer``. It can be overridden
for special product requirements, but for a standard applications, the default implementation
should just work out of the box.

During development, it can be useful to examine what data this serializer delivers. The easiest way
to achieve this, is to append ``/add-to-cart?format=api`` to the URL on the product's detail view.
This will show the interface with which the add-to-cart form communicates.

Ensure that the context for rendering a product contains the key ``product`` referring to the
product object – this is the default behavior. Then add

.. code-block:: django

	{% include "shop/catalog/product-add2cart.html" %}

to an appropriate location in the template which renders the product detail view.

The now included add-to-cart template contains a form with some input fields and a few AngularJS
directives, which communicate with the endpoint connected to the ``AddToCartSerializer``. It
updates the subtotal whenever the customer changes the quantity and optionally displays a nice
popup window, whenever an item is added to the cart. Of course, that template can be extended with
arbitrary HTML.

These Angular JS directives require some JavaScript code which is located in the file
``shop/js/catalog.js``; it is referenced automatically when using the above template include
statement.

.. [#add2cart] Specially in business-to-business sites, this usually is done in the list views.


Understanding the Routing
=========================

Behind the scenes, **django-CMS** allows us to attach Django Views to any existing CMS page using
a so called apphook_. This means, that accessing a CMS page or any child ot it, can implicitely
invoke a Django View. To achieve this, in the CMS page's *Advanced Settings*, that *apphook* must
be selected from the drop-down menu named "Application".

In our implementation, such an *apphook* can be implemented as:

.. code-block:: python

	from django.conf.urls import url
	from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView
	from shop.cms_apphooks import CatalogListCMSApp

	class CatalogListApp(CatalogListCMSApp):
	    def get_urls(self, page=None, language=None, **kwargs):
	        return [
	            url(r'^$', ProductListView.as_view()),
	            url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view()),
	            url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
	        ]

	apphook_pool.register(CatalogListApp)

All what this apphook does, is to set special routes to either, the catalog's list view, here
:class:`shop.views.catalog.ProductListView`, or to the product's detail view, here
:class:`shop.views.catalog.ProductRetrieveView`, or to the add-to-cart view, here
:class:`shop.views.catalog.AddToCartView`.

Such an apphook allows us to extend an existing CMS page with classic Django Views routed onto
sub-URLs of our page. Here we create additional routes, on top of the existing CMS page. These
three views also serve another purpose: They enrich the rendering context by a Python dictionary
named ``product``, it contains the serialized representation to render the corresponding templates.

.. _apphook: http://docs.django-cms.org/en/latest/how_to/apphooks.html


Next Chapters
=============

One of the unique features of **django-SHOP**, is the possibility to choose and/or override its
product models. Depending on the kind of product model selected through the cookiecutter template,
proceed with one of the following chapters from one of these tutorials:

* :ref:`tutorial/product-model-commodity`
* :ref:`tutorial/product-model-smartcard`
* :ref:`tutorial/product-model-polymorphic`
