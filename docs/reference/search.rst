.. _reference/search:

================
Full Text Search
================

How should a customer find the product he desires in a more or less unstructured collection of
countless products? Hierarchical navigation often doesn't work and takes too much time. Thanks to
the way we use the Internet today, most site visitors expect one central search field in, or nearby
the main navigation bar of a site.


Search Engine API
=================

In Django the most popular API for full-text search is Haystack_. While other indexing backends,
such as Solr and Whoosh might work as well, the best results have been achieved with Elasticsearch_.
Therefore this documentation focuses exclusively on Elasticsearch. And since in **django-SHOP** every
programming interface uses REST, search is no exception here. Fortunately there is a project named
drf-haystack_, which "restifies" our search results, if we use a special serializer class.

In this document we assume that the merchant only wants to index his products, but not any arbitrary
content, such as for example the terms and condition, as found outside **django-SHOP**, but inside
**django-CMS**. The latter would however be perfectly feasible.


Configuration
-------------

Install the Elasticsearch binary. Currently Haystack only supports versions smaller than 2. Then
start the service in daemon mode:

.. code-block:: shell

	./path/to/elasticsearch-version/bin/elasticsearch -d

Check if the server answers on HTTP requests. Pointing a browser onto port http://localhost:9200/
should return something similar to this:

.. code-block:: shell

	$ curl http://localhost:9200/
	{
	  "status" : 200,
	  "name" : "Ape-X",
	  "cluster_name" : "elasticsearch",
	  "version" : {
	    ...
	  },
	}

In ``settings.py``, check that ``'haystack'`` has been added to ``INSTALLED_APPS`` and connects
the application server with the Elasticsearch database:

.. code-block:: python

	HAYSTACK_CONNECTIONS = {
	    'default': {
	        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
	        'URL': 'http://localhost:9200/',
	        'INDEX_NAME': 'myshop-default',
	    },
	}

In case we need indices for different natural languages on our site, we shall add the non-default
languages to this Python dictionary using a different ``INDEX_NAME`` for each of them.

Finally configure the site, so that search queries are routed to the correct index using the
currently active natural language:

.. code-block:: python

	HAYSTACK_ROUTERS = ('shop.search.routers.LanguageRouter',)


Indexing the Products
=====================

Before we start to search for something, we first must populate its indices. In Haystack one can
create more than one kind of index for each item being added to the search database.

Each product type requires its individual indexing class. Note that Haystack does some
autodiscovery, therefore this class must be added to a file named ``search_indexex.py``. For our
product model ``SmartCard``, this indexing class then may look like:

.. code-block:: python
	:caption: myshop/search_indexes.py
	:name: smartcard-search-indexes

	from shop.search.indexes import ProductIndex
	from haystack import indexes

	class SmartCardIndex(ProductIndex, indexes.Indexable):
	    catalog_media = indexes.CharField(stored=True,
	        indexed=False, null=True)
	    search_media = indexes.CharField(stored=True,
	        indexed=False, null=True)

	    def get_model(self):
	        return SmartCard

	    # more methods ...

While building the index, Haystack performs some preparatory steps:


Populate the reverse index database
-----------------------------------

The base class for our search index declares two fields for holding the reverse indexes and a few
additional fields to store information about the indexed product entity:

.. code-block:: python
	:caption: shop/indexes.py

	class ProductIndex(indexes.SearchIndex):
	    text = indexes.CharField(document=True,
	        indexed=True, use_template=True)
	    autocomplete = indexes.EdgeNgramField(indexed=True,
	        use_template=True)

	    product_name = indexes.CharField(stored=True,
	        indexed=False, model_attr='product_name')
	    product_url = indexes.CharField(stored=True,
	        indexed=False, model_attr='get_absolute_url')

The first two `index fields`_ require a template which renders plain text, which is used to build a
reverse index in the search database. The ``indexes.CharField`` is used for a classic reverse text
index, whereas the ``indexes.EdgeNgramField`` is used for autocompletion_.

Each of these index fields require their own template. They *must* be named according to the
following rules:

.. code-block:: guess

	search/indexes/myshop/<product-type>_text.txt

and

.. code-block:: guess

	search/indexes/myshop/<product-type>_autocomplete.txt

and be located inside the project's template folder. The ``<product-type>`` is the classname in
lowercase  of the given product model. Create two individual templates for each product type, one
for text search and one for autocompletion.

An example:

.. code-block:: django
	:caption: search/indexes/smartcard_text.txt

	{{ object.product_name }}
	{{ object.product_code }}
	{{ object.manufacturer }}
	{{ object.description|striptags }}
	{% for page in object.cms_pages.all %}
	{{ page.get_title }}{% endfor %}

The last two fields are used to store information about the product's content, side by side with the
indexed entities. That's a huge performance booster, since this information otherwise would have to
be fetched from the relational database, item by item, and then being rendered while preparing the
search query result.

We can also add fields to our index class, which stores pre-rendered HTML. In the above example,
this is done by the fields ``catalog_media`` and ``search_media``. Since we do not provide
a model attribute, we must provide two methods, which creates this content:

.. code-block:: python
	:caption: myshop/search_indexes.py
	:name: searchindex-media

	class SmartCardIndex(ProductIndex, indexes.Indexable):
	    # other fields and methods ...

	    def prepare_catalog_media(self, product):
	        return self.render_html('catalog', product, 'media')

	    def prepare_search_media(self, product):
	        return self.render_html('search', product, 'media')

These methods themselves invoke ``render_html`` which takes the product and renders it using
a templates named ``catalog-product-media.html`` or ``search-product-media.html`` respectively.
These templates are looked for in the folder ``myshop/products`` or, if not found there in the
folder ``shop/products``. The HTML snippets for catalog-media are used for autocompletion search,
whereas search-media is used for normal a normal full-text search invocation.


Building the Index
------------------

To build the index in Elasticsearch, invoke:

.. code-block:: shell

	./manage.py rebuild_index --noinput

Depending on the number of products in the database, this may take some time.


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
.. _drf-haystack: https://pypi.python.org/pypi/drf-haystack
.. _Haystack for Django REST Framework: https://drf-haystack.readthedocs.org/en/latest/
.. _normalized: https://www.elastic.co/guide/en/elasticsearch/guide/current/token-normalization.html
.. _index fields: http://django-haystack.readthedocs.org/en/latest/searchfield_api.html
.. _autocompletion: http://django-haystack.readthedocs.org/en/latest/autocomplete.html?highlight=autocompletion
.. _djangoCMS apphook: http://docs.django-cms.org/en/stable/how_to/apphooks.html
