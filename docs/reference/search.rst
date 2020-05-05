.. _reference/search:

================
Full Text Search
================

How should a customer find the product he desires in a more or less unstructured collection of
countless products? Hierarchical navigation often doesn't work and takes too much time. Thanks to
the way we use the Internet today, most site visitors expect one central search field inside, or
nearby the main navigation bar of a site.


Search Engine API
=================

While it is possible to adopt other search backends to **django-SHOP** with little effort, this
documentation focuses exclusively on Elasticsearch_.

Until version 1.1, **django-SHOP** used Haystack_. Haystack is a great third party app for Django
and easy to adapt for full-text search. Unfortunately, Haystack was never adopted to versions
of Elasticsearch beyond 1.7. Also, it didn't allow complicated queries and the configuration is
minimal and highly restricted. Therefore, **django-SHOP** version 1.2 has been refactored to use
elasticsearch-dsl_ together with django-elasticsearch-dsl_. It now supports up to the most recent
version of Elasticsearch, which currently is 7.6.

In this document we assume that the merchant only wants to index his products, but not any arbitrary
content, such as for example the terms and condition, as found outside **django-SHOP**, but inside
**django-CMS**. The latter would however be perfectly feasible.


Configuration
-------------

Download and install the latest version of the Elasticsearch binary. During development, all tests
have been performed with version 7.5. After unzipping the file, start Elasticsearch in daemon mode:

.. code-block:: shell

	./path/to/elasticsearch-version/bin/elasticsearch -d

Check if the server answers on HTTP requests. Pointing a browser onto port http://localhost:9200/
should return something similar to this:

.. code-block:: shell

	$ curl http://localhost:9200/
	{
	  "name" : "Ape-X",
	  "cluster_name" : "elasticsearch",
	  "cluster_uuid" : "P9HVZRPbUXjTEDO9iZHGDk",
	  "version" : {
	    ...
	  },
	}

Install ``elasticsearch-dsl`` and ``django-elasticsearch-dsl`` using the ``pip`` command or another
tool of your choice.

In ``settings.py``, check that ``'django_elasticsearch_dsl'`` has been added to ``INSTALLED_APPS``.
Configure the connection to the Elasticsearch database:

.. code-block:: python

	ELASTICSEARCH_DSL = {
	    'default': {
	        'hosts': 'localhost:9200',
	    },
	}


Indexing the Products
=====================

Before adding search support for products on our site, we must consider which fields of our product
model contain relevant information to be searched for. The philosophy of **django-SHOP** is to not
impose any predefined fields for this purpose, but rather let the merchants decide what they need.
Therefore it is quite important to spot the fields in the product models, which contain the relevant
information customers might search for.

Elasticsearch uses the term ``Document`` to describe a searchable entity. In **django-SHOP**, we
can define one or more product models, each declaring their own fields. Since in our shop we want
to search over all products, regardless of their specific model definition, we need a mapping from
those fields onto the representation used to create the reverse index. For this purpose,
**django-SHOP** is shipped with a generic document class named ``ProductDocument``. It contains
three index fields: ``product_name``, ``product_code`` and ``body``.


Product Name
------------

The product's name often is declared as a ``CharField`` in our product's model. Depending on the
nature of the product, it could also be declared for different languages. Using django-parler's
``TranslatableField``, the product name then is stored in a Django model related to the product
model. We also want to ensure, that this name is indexed only for a specific language. This
information is stored inside the ``Document`` field ``product_name``.


Product Code
------------

The product's code remains the same for all languages. However, in case a product is offerend in
different variants, each of them may declare their own code. This means, that the same product can
be found through one or more product codes. Moreover, since product code are unique identifiers,
we usually do not want to apply stemming, they are stored as a list of keywords inside an
Elasticsearch ``Document`` entity.


Body Field
----------

Depending on our product's model declaration, we can have many additional fields containing
information, which may be relevant to be searched for. Therefore the merchant must declare a Django
template for each product type. This template then is used to render the content of those fields as
plain text. This text is never seen by the customer, but rather used to feed our full text search
engine when building the reverse index. First Elasticsearch strips all HTML tags from that text.
In the second step, this text is tokenized and stemmed by Elasticsearch analyzers. In
**django-SHOP** we can specify one analyzer for each language.


Example
.......

Say, we have a product using this simplified model representation:

.. code-block:: python

	from django.db import models
	from shop.models.product import BaseProduct

	class Author(models.Model):
	    name = models.CharField(
	        _("Author Name"),
	        max_length=255,
	    )

	class Editor(models.Model):
	    name = models.CharField(
	        _("Editor"),
	        max_length=255,
	    )

	class Book(BaseProduct):
	    product_name = models.CharField(
	        _("Book Title"),
	        max_length=255,
	    )

	    product_code = models.CharField(
	        _("Product code"),
	        max_length=255,
	    )

	    caption = HTMLField(
	        help_text=_("Short description"),
	    )

	    authors = models.ManyToManyField(Author)

	    editor = models.ForeignKey(
	        Editor,
	        on_delete=models.CASCADE,
	    )

By default, **django-SHOP** only indexes the fields ``product_name`` and ``product_code``. However,
we also want all other fields beeing indexed. If the merchant's project is named
``awesome_bookstore``, then inside the project's template folder, we must create a file named
``awesome_bookstore/search/indexes/book.txt``. This template file then shall contain:

.. code-block:: text
	:caption: awesome_bookstore/search/indexes/book.txt

	{{ product.caption }}
	{% for author in product.authors.all %}
	{{ author.name }}{% endfor %}
	{{ product.editor.name }}

When building the index, this template is rendered for each product in our bookstore. The rendered
content then cleaned up, tokenized, stemmed, filtered and used to build the reverse index for the
Elasticsearch database. The reverse index then is stored in the ``body`` field inside the
:class:`shop.search.documents.ProductDocument`.

If the above template file can not be found, **django-SHOP** falls back onto
``awesome_bookstore/search/indexes/product.txt``. If that template file is missing too, then
the file ``shop/search/indexes/product.txt`` is used. Note that the template file always is in
lowercase.


Populate the Database
---------------------

To build the index in Elasticsearch, invoke:

.. code-block:: shell

	./manage.py search_index --rebuild

Depending on the number of products in the database, this may take some time.




Building the Index
------------------



Search Serializers
==================

`Haystack for Django REST Framework`_ is a small library aiming to simplify using Haystack with
Django REST Framework. It takes the search results returned by Haystack, treating them the similar
to Django database models when serializing their fields. The serializer used to render the content
for this demo site, may look like:

.. code-block:: python
	:caption: myshop/serializers.py
	:name: serializers

	from rest_framework import serializers
	from shop.search.serializers import ProductSearchSerializer as ProductSearchSerializerBase
	from .search_indexes import SmartCardIndex, SmartPhoneIndex

	class ProductSearchSerializer(ProductSearchSerializerBase):
	    media = serializers.SerializerMethodField()

	    class Meta(ProductSearchSerializerBase.Meta):
	        fields = ProductSearchSerializerBase.Meta.fields + ('media',)
	        index_classes = (SmartCardIndex, SmartPhoneIndex)

	    def get_media(self, search_result):
	        return search_result.search_media

This serializer is part of the project, since we must adopt it to whatever content we want to
display on our site, whenever a visitor enters some text into the search field.


.. _reference/search-view:

Search View
===========

In the Search View we link the serializer together with a `djangoCMS apphook`_. This
``CatalogSearchApp`` can be added to the same file, we already used to declare the
``CatalogListApp`` used to render the catalog view:

.. code-block:: python
	:caption: myshop/cms_apps.py
	:name: search-app

	from cms.apphook_pool import apphook_pool
	from shop.cms_apphooks import CatalogSearchCMSApp

	class CatalogSearchApp(CatalogSearchCMSApp):
	    def get_urls(self, page=None, language=None, **kwargs):
	        return ['myshop.urls.search']

	apphook_pool.register(CatalogSearchApp)

as all apphooks, it requires a file defining its urlpatterns:

.. code-block:: python
	:caption: myshop/urls/search.py

	from django.conf.urls import url
	from shop.search.views import SearchView
	from myshop.serializers import ProductSearchSerializer

	urlpatterns = [
	    url(r'^', SearchView.as_view(
	        serializer_class=ProductSearchSerializer,
	    )),
	]


Display Search Results
----------------------

As with all other pages in **django-SHOP**, the page displaying our search results is a normal CMS
page too. It is suggested to create this page on the root level of the page tree.

As the page title use "*Search*" or whatever is appropriate as expression. Then we change into
the *Advanced Setting* od the page.

As a template use one with a big placeholder, since it must display our search results. Our default
template usually is a good fit.

As the page **Id** field, enter ``shop-search-product``. Some default HTML snippets, prepared for
inclusion in other templates, use this hard coded string.

Set the input field **Soft root** to checked. This hides our search results page from the menu list.

As **Application**, select "*Search*". This selects the apphook we created in the previous section.

Then save the page, change into **Structure** mode and locate the placeholder named
**Main Content**. Add a Bootstrap Container plugin, followed by a Row and then a Column plugin. As
the child of this column, choose the **Search Results** plugin from section **Shop**.

Finally publish the page and enter some text into the search field. It should render a list of
found products.

|product-search-results|

.. |product-search-results| image:: /_static/product-search-results.png


.. _reference/search-autocompletion-catalog:

Autocompletion in Catalog List View
===================================

As we have seen in the previous example, the Product Search View is suitable to search for any item
in the product database. However, the site visitor sometimes might just refine the list of items
shown in the catalog's list view. Here, loading a new page which uses a layout able to render every
kind of product usually differs from the catalog's list layout, and hence may by inappropriate.

Instead, when someone enters some text into the search field, **django-SHOP** starts to narrow down
the list of items in the catalog's list view by typing query terms into the search field. This is
specially useful in situations where hundreds of products are displayed together on the same page
and the customer needs to pick out the correct one by entering some search terms.

To extend the existing Catalog List View for autocompletion, locate the file containing the
urlpatterns, which are used by the apphook ``ProductsListApp``. In doubt, consult the file
``myshop/cms_apps.py``. This apphook names a file with urlpatterns. Locate that file and add the
following entry:

In order to use the Product Search View, our Product Model must inherit from
:class:`shop.models.product.CMSPageReferenceMixin`. This is because we must add a reference to the
CMS pages our products are assigned to, into the search index database. Such a product may for
instance be declared as:

.. code-block:: python

	from shop.models.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin

	class MyProduct(CMSPageReferenceMixin, BaseProduct):
	    ...

	    objects = BaseProductManager()

	    ...

We normally want to use the same URL to render the catalog's list view, as well as the
autocomplete view, and hence must route onto the same view class. However the search- and the
catalog's list view classes have different bases and a completely different implementation.

The normal List View uses a Django queryset to iterate over the products, while the autocomplete
View uses a Haystack Search queryset. Therefore we wrap both View classes into
:class:`shop.search.views.CMSPageCatalogWrapper` and use it in our URL routing such as:

.. code-block:: python

	from django.conf.urls import url
	from shop.search.views import CMSPageCatalogWrapper
	from myshop.serializers import CatalogSearchSerializer

	urlpatterns = [
	    url(r'^$', CMSPageCatalogWrapper.as_view(
	        search_serializer_class=CatalogSearchSerializer,
	    )),
	    # other patterns
	]

The view class ``CMSPageCatalogWrapper`` is a functional wrapper around the catalog's products list
view and the search view. Depending on whether the request contains a search query starting with
``q=<search-term>``, either the search view or the normal products list view is invoked.

The ``CatalogSearchSerializer`` used here is very similar to the ``ProductSearchSerializer``, we
have seen in the previous section. The only difference is, that instead of the ``search_media``
field is uses the ``catalog_media`` field, which renders the result items media in a layout
appropriate for the catalog's list view. Therefore this kind of search, normally is used in
combination with auto-completion, because here we reuse the same layout for the product's list view.


The Client Side
---------------

To facilitate the placement of the search input field, **django-SHOP** ships with a reusable
AngularJS directive ``shopProductSearch``, which is declared inside the module
``shop/js/search-form.js``.

A HTML snipped with a submission form using this directive can be found in the shop's templates
folder at ``shop/navbar/search-form.html``. If you override it, make sure that the form element
uses the directive ``shop-product-search`` as attribute:

.. code-block:: django

	<form shop-product-search method="get" action="/url-of-page-rendering-the-search-results">
	  <input name="q" ng-model="searchQuery" ng-change="autocomplete()" type="text" />
	</form>

If you don't use the prepared HTML snippet, assure that the module is initialized while
bootstrapping our Angular application:

.. code-block:: javascript

	angular.module('myShop', [..., 'django.shop.search', ...]);


.. _Haystack: http://haystacksearch.org/
.. _Elasticsearch: https://www.elastic.co/
.. _elasticsearch-dsl: https://elasticsearch-dsl.readthedocs.io/en/latest/
.. _django-elasticsearch-dsl: https://django-elasticsearch-dsl.readthedocs.io/en/latest/
.. _normalized: https://www.elastic.co/guide/en/elasticsearch/guide/current/token-normalization.html
.. _djangoCMS apphook: http://docs.django-cms.org/en/stable/how_to/apphooks.html
