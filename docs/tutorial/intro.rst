.. _tutorial/intro:

========
Tutorial
========

This tutorial is aimed at people new to django SHOP but already familiar with Django. If you aren't
yet, reading their excellent `Django Tutorial`_ is highly recommended.

Since **django-SHOP** relies on many features offered by **django-CMS** and **Django REST Framework**,
you should familiarize yourself with these apps.


Introduction
============

**Django-SHOP** is an e-commerce framework rather than a turn-key solution. Therefore beginners
are strongly recommended to start with one of the provided examples. These demos are what we
describe as the "*merchant implementation*". Here merchants provide their product models, templates
and everything else, which is required to get their customized shop up and running. This approach
allows us to implement every desired extra feature, without having to implement everything from
scratch.

Currently **django-SHOP** is shipped with 6 merchant demo implementations:

* :ref:`tutorial/product-model-commodity` and :ref:`tutorial/product-model-i18n_commodity`
* :ref:`tutorial/product-model-smartcard` and :ref:`tutorial/product-model-i18n_smartcard`
* :ref:`tutorial/product-model-polymorphic` and :ref:`tutorial/product-model-i18n_polymorphic`

You may install them manually and populate their content yourself. The recommended way however,
is to install them manually, and :ref:`tutorial/populate-database-fixtures`.

If you have a Docker runtime on your workstation, an even quicker approach is to
:ref:`tutorial/quickstart`.


.. _tutorial/prepare-installation:

Prepare the Installation
========================

To run the examples shown in this tutorial, you must install **django-SHOP** from GitHub, since
the pip-installable from PyPI only contains the framework, but not the files required for the demos.
Before proceeding, please make sure virtualenv_ is installed on your system, otherwise you would
pollute your Python site-packages folder.

Because we are using the current Github master for this tutorial, you must also
use the documentation for the current Github master. If you are reading this
document on Read The Docs, please look for the version selector (usually at the
bottom of the screen) and select "latest".

Also ensure that these packages are installed using the favorite package manager of your operating
system:

* Python 2.7, 3.5 or 3.6 (recommended)
* Redis: http://redis.io/
* SQLite: https://www.sqlite.org/
* Node Package Manager: https://www.npmjs.com/
* Optionally Elasticsearch version 1.7.5 (not later)

.. code-block:: shell

	$ mkdir Tutorial; cd Tutorial
	$ virtualenv -p $(which python3) shoptutorial
	$ source shoptutorial/bin/activate
	(shoptutorial)$ pip install -U pip setuptools
	(shoptutorial)$ git clone --depth 1 https://github.com/awesto/django-shop
	(shoptutorial)$ cd django-shop
	(shoptutorial)$ pip install 'Django<2.0' 'django-select2<6.1' 'django-angular<2.1'
	(shoptutorial)$ pip install -r requirements/common.txt
	(shoptutorial)$ pip install --no-deps -e .
	(shoptutorial)$ cd example
	(shoptutorial)$ npm install

These statements will setup an environment that runs one of the demo shops out of the box.

.. note:: We recommend that you use Python 3, but if you stuck with Python-2.7, please note that
	you have to additionally invoke ``pip install enum34 funcsigs``.


.. _tutorial/create-demo-database:

Create a database for the demo
------------------------------

Finally we must create a database to run our example project:

.. code-block:: shell

	(shoptutorial)$ cd django-shop/example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=commodity DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py createsuperuser
	Email address: admin@example.org
	Username: admin
	Password:
	Password (again):
	Superuser created successfully.
	(shoptutorial)$ ./manage.py runserver

If Elasticsearch is installed and running, optionally build the search index:

.. code-block:: shell

	(shoptutorial)$ ./manage.py rebuild_index

Finally point a browser onto http://localhost:8000/ and log in as the superuser you just created.

Presumably you are somehow disappointed now, because there is only one empty page served by the CMS
and no pages for the catalog, the cart, the checkout and the orders – yet! In **django-SHOP** this
is by intention, because we prefer to arrange our web components inside the CMS rather than using
hard coded templates.

For gaining a first impression of **django-SHOP**, this can be quite annoying. Therefore it is
recommended to :ref:`tutorial/populate-database-fixtures`.


.. _tutorial/populate-database-fixtures:

Populate the Database using Fixtures
------------------------------------

Unless you want to populate the shop from scratch with your own categories, products, and pages for
the cart, checkout and order views, then proceed with one of the prepared fixtures. There is one
fixture file and a folder of media files for each demo. These files are not shipped within the
repository, but downloaded separately from the Internet using these commands:

.. code-block:: shell

	(shoptutorial)$ cd django-shop/example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=commodity DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py initialize_shop_demo
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/ and wait a few minutes until the files are loaded
into the database.

This runs the demo for :ref:`tutorial/product-model-commodity`. By changing the environment
variable ``DJANGO_SHOP_TUTORIAL`` to ``i18n_commodity``, ``smartcard``, ``i18n_smartcard``,
``polymorphic`` or ``i18n_polymorphic``, you can examine one of the other prepared examples.
Afterwards re-run ``./manage.py initialize_shop_demo`` for each of them.

All demos can be started independently from each other, but you are encouraged to begin with the
``commodity`` example, and then proceed to the more complicate ones.

.. note:: The first time, **django-SHOP** renders a page, images must be thumbnailed and cropped.
	This is an expensive operation which runs only once. Therefore please be patient, when loading
	pages for the first time.


.. _tutorial/add-pages-cms:

Adding pages to the CMS
=======================

Before adding pages or products, we must sign in as a Django staff user. If our demo has been
loaded through one of the prepared fixtures, use user *admin* with password *secret*. After
signing in, a small arrow appears on the top right in our browser. Clicking on that arrow expands
the Django-CMS toolbar.

|django-cms-toolbar|

.. |django-cms-toolbar| image:: /_static/tutorial/django-cms-toolbar.png

Click on the menu item named **example.com** and select **Pages ...**. This opens the Django-CMS
*Page Tree*.  In **django-SHOP**, every page, can be rendered by the CMS. Therefore, unless we
need a special landing page, we can start immediately with the *Catalog's List View* of our
products. The demos ``commodity``, ``i18n_commodity``, ``smartcard`` and ``i18n_smartcard`` are
configured in such a way.

Click on **New Page** to create a new Page. As its **Title** choose "Catalog" or whatever seems
appropriate. Then change into the **Advanced Settings** at the bottom of the page. In this editor
window, locate the field **Template** and choose the default.

Since we want to attach the products list view to our page, we must select **Catalog List** from
the drop down menu named **Application**. Then save the page and click on **View on site**.

.. note:: In the demos ``commodity`` and ``i18n_commodity``, the Catalog List View redirects
	onto its lonely product, therefore we can't access that page – yet. More on that later.

Change into **Structure** mode and locate the placeholder named **Main Content**.
Add a plugin from section **Bootstrap** named **Row**. Below that Row add a Column with a width of
12 units. Finally, below the last Column add a plugin from section **Shop** named **Catalog List
View**.

Now we have a working catalog list view, but since we haven't added any products to the database
yet, we won't see any items on our page.


Understanding the Routes
------------------------

Behind the scenes, **django-CMS** allows us to attach Django Views to any existing CMS page.
In our implementation, such a routing can be implemented as:

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

This is all, what our Catalog List View does and in **django-CMS**, this is named an apphook_.
Such an apphook allows us to extend an existing CMS page with classic Django Views routed onto
sub-URLs of our page. Here we create additional routes, but these three views also serve another
purpose: The enrich the rendering context by a Python dictionary named ``data``. This dictionary
contains everything we need to render our catalog's list- or detail-view and can be accessed by
the rendering templates.


.. _tutorial/product-model-commodity:

The Commodity Product Model
===========================

The ``commodity`` demo shows how to setup a monolingual shop, with a single generic product, named
**Commodity**. The product model :class:`shop.models.defauls.commodity.Commodity` is part of the
**django-SHOP** framework. It is intended for shops where the merchant does not want to create a
customized product model, but rather prefers to create the product's detail views using common CMS
functionality. Here for demonstration purpose we try to sell a house, hence it is practical that we
can layout our CMS page the way we want to and we can add whatever Django-CMS plugins are available.

A **Commodity** model contains only the following attributes:

* The name of the product.
* The product code.
* The slug_ (a short label used as the last bit in the URLs).
* The product's unit price.
* One sample image to be shown in the catalog's list view.
* A caption to be shown in the catalog's list view.

The detail view for each product must however be styled individually using a **django-CMS**
placeholder together with the plugin system provided, for instance by djangocms-cascade_. This
gives the merchant all the flexibility to style each product's detail page individually and without
having to create a special HTML template. Into the provided placeholder we then can add as many
text fields as we want. Additionally we can use image galleries, carousels, different backgrounds,
tab sets, etc.

One plugin which should always be present on a product's detail page, is the **Add Product to Cart**
plugin as found in section **Shop**. Otherwise a customer wouldn't be able to add that product to
the cart and thus purchasing anything.

Using the **Commodity** product model only makes sense, if the merchant does not require special
product attributes and normally is only suitable for shops with up to a dozen articles. Otherwise,
creating a reusable HTML template is probably less effort, than filling the placeholder for each
product's detail page individually.

The ``commodity`` demo contains just one product, a splendid villa. In such a situation, we usually
don't want to render the catalogs list view, but instead want to get redirected onto our lonely
product. Therefore, by rewriting our catalogs list view to
``ProductListView.as_view(redirect_to_lonely_product=True)``, we can instruct the router to behave so.


.. _tutorial/product-model-i18n_commodity:

The Internationalized Commodity Product Model
=============================================

The ``i18n_commodity`` demo shows how to setup a shop, with the same generic product as in the
previous example. However, these attributes now are translatable into multiple natural languages:

* The name of the product.
* The slug.
* A caption to be shown in the catalog's list view.

Using this internationalized version, requires to configure ``I18N = True`` in our ``settings.py``.
Additionally we must install django-parler_. By doing so, the product model from above
:class:`shop.models.defauls.commodity.Commodity`, is replaced by an internationalized version.

All other product attributes, such as unit price and product code are shared across all languages.


.. _tutorial/product-model-smartcard:

The Smart Card Product Model
============================

The ``smartcard`` demo shows how to setup a shop with a model, created explicitly to describe a
certain type of product. Smart Cards have many different attributes such as their card type, the
manufacturer, storage capacity and the maximum transfer speed. Here it's the merchant's
responsibility to create the database model according to the physical properties of the product.

The class :class:`myshop.models.smartcard.SmartCard` therefore is not part of the shop's framework,
but rather in the merchant's implementation as found in our example.

Creating a customized product model is only a few lines of declarative Python code. Additionally we
have to create a Django template using HTML. It however keeps us from having to build a page using
plugins, for each product item we want to offer. It also helps us to structure our products using
attributes rather than describing them in a free form.


.. _tutorial/product-model-i18n_smartcard:

The Internationalized Smart Card Model
======================================

The ``i18n_smartcard`` demo is a variation of the above example, with a few attributes translated
into multiple languages, namely ``caption`` and ``description``. The product name of a Smart Card
is international anyways and doesn't require to be translated into different langauges. Hence we
don't require a translatable field for the product name and its slug.


.. _tutorial/product-model-polymorphic:

The Polymorphic Product Model
=============================

The ``polymorphic`` demo is a combination from all of the examples from above. Here we declare a
base product model using the class :class:`myshop.models.polymorphic_.Product`. We also declare
common fields available in all of our different product types. These fields act as the smallest
common denominator for the views where we want to display summary information about our products,
independently of their characteristics. This generally is the product's name, a thumbnailed image,
the price and often a caption.

List views showing a summary information about our products are the *Cart View*, the *Order Detail
View* and eventually the *Catalog List View*.

The model classes for Smart Card, Smart Phone and a variation of Commodity then inherits from this
base product class. These models additionally can declare attributes required to describe the
physical properties of each product type. Since they vary, we also have to create special templates
for the detail views of each of them. Smart Phones for instance allow product variations, therefore
we must adopt the template for adding the product to the cart.


.. _tutorial/product-model-i18n_polymorphic:

The Internationalized Polymorphic Product Model
===============================================

The ``i18n_polymorphic`` demo is a variation of the above example, with a few attributes translated
into multiple languages, namely ``caption`` and ``description``. This sample implementation does not
use translated slugs, although it would be possible.


Use one of the demos as a starting point for your project
=========================================================

Depending on the needs of your e-commerce site, the easiest approach to start with your
implementation of **django-SHOP**, is to use one of the six demo samples from above:

* If you only require a free form product description, go ahead with the ``commodity`` or
  ``i18n_commodity`` sample.
* If you need a shop with one specific product type, then go ahead with the ``smartcard`` or
  ``i18n_smartcard`` sample. Rename the product model to whatever makes sense and add additional
  fields to describe the properties of your model.
* If you need a shop with different product types, then go ahead with the ``polymorphic`` or
  ``i18n_polymorphic`` sample. Specify the common fields in the product's base class and
  add additional fields to describe the properties each of your product model.

It also is suggested to reuse the current structure of CMS pages and placeholders from the given
samples. Having a working implementation, it is much easier to gradually modify it, until you reach
a final goal, rather than starting with an empty site from scratch.

.. _Django Tutorial: https://docs.djangoproject.com/en/stable/intro/tutorial01/
.. _apphook: http://docs.django-cms.org/en/latest/topics/apphooks.html
.. _django-parler: http://django-parler.readthedocs.org/en/latest/
.. _polymorphism: https://django-polymorphic.readthedocs.org/en/latest/
.. _slug: https://docs.djangoproject.com/en/stable/glossary/#glossary
.. _djangocms-cascade: http://djangocms-cascade.readthedocs.io/en/latest/
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
