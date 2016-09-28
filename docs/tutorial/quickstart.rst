.. _tutorial/quickstart:

=========================
Quickstart a Running Demo
=========================

Running Demos Locally
=====================

You may download all dependencies and start the testing projects manually. If you want to use the
demo as a starting point for your own project, then this presumably is the better solution.

Filling your CMS with page content and adding products is a boring job. Impatient users can start
with one of the five provided demos, using prepared sample data. First assure that all dependencies
are installed into it's virtual environment as described in section :ref:`tutorial/prepare-installation`.
Then instead of adding pages and products manually, use the following steps:

.. code-block:: shell

	(shoptutorial)$ cd django-shop/example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=commodity
	(shoptutorial)$ ./manage.py initialize_shop_demo
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and sign in as user *admin* with password
*secret*.

This runs the demo for :ref:`tutorial/commodity`.

.. note:: The first time, **djangoSHOP** renders a page, images must be thumbnailed and cropped.
	This is an expensive operation which runs only once. Therefore please be patient, when loading
	pages for the first time.

Starting from this folder, you can run all five demos by reconfiguring the environment variable
``DJANGO_SHOP_TUTORIAL``. Allowed values are ``commodity``, ``i18n_commodity``, ``smartcard``,
``i18n_smartcard`` and ``polymorphic``. Afterwards re-run ``./manage.py initialize_shop_demo``
for each of them.

.. note:: All demos can be started independently from each other, but you are encouraged to begin
	with the ``commodity`` example, and then proceed to the more complicate ones.

.. _tutorial/commodity:

The Commodity Product Model
---------------------------

The ``commodity`` demo shows how to setup a monolingual shop, with a generic product, named
**Commodity**. The product model :class:`shop.models.defauls.commodity.Commodity` is part of the
**djangoSHOP** framework. It is intended for shops where the merchant does not want to create a
customized product model, but rather prefers to create the product's detail views using common CMS
functionality.

A **Commodity** model contains only the following attributes:

* The name of the product
* The product code
* The slug (a short label used as the last bit in the URLs)
* The product's unit price
* One sample image to be shown in the catalog's list view
* A caption to be shown in the catalog's list view

The detail view for each product must however be styled individually using a DjangoCMS placeholder
together with the plugin system provided by djangocms-cascade_. This gives the merchant all the
flexibility to style each product's detail page individually and without having to create a special
HTML template. Into the provided placeholder we then can add as many text fields as we want.
Additionally we can use image galleries, carousels, different backgrounds, tab sets, etc.

One plugin which should always be present is the **Add Product to Cart** plugin as found in section
**Shop**, otherwise a customer wouldn't be able to add that product to the cart and thus purchasing
anything.

Using the **Commodity** product model only makes sense, if the merchant does not require special
product attributes and normally is only suitable for shops with up to a dozen articles. Otherwise,
creating a reusable HTML template is probably less effort, than filling the placeholder for each
product's detail page individually.


The Internationalized Commodity Product Model
---------------------------------------------

The ``i18n_commodity`` demo shows how to setup a shop, with the same generic product as in the
previous example, but with these attributes translatable into multiple natural languages:

* The name of the product
* The slug
* A caption to be shown in the catalog's list view

All other product attributes from our **Commodity** model are shared across all languages.

Using this internationalized configuration, requires to additionally install django-parler_.


The Smart Card Product Model
----------------------------

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


The Internationalized Smart Card Model
--------------------------------------

The ``i18n_smartcard`` demo is a variation of the above example, with a few attributes translated
into multiple languages, namely ``caption`` and ``description``. The product name of a Smart Card
is international anyways and doesn't require to be translated into different langauges. Hence we
don't require a translatable field for the product name and it's slug.


The Polymorphic Product Model
-----------------------------

The ``polymorphic`` demo is a combination from all of the examples from above. Here we declare a
base product model using the class :class:`myshop.models.polymorphic.Product`. We also declare
common fields available in all of our different product types. These common fields are used to build
up the view displaying a list of all products.

The model classes for Smart Card, Smart Phone and a variation of Commodity then inherit from this
base product class. These models additionally can declare attributes required to describe the
physical properties of each product type. Since they vary, we also have to create special templates
for the detail views of each of them. Since Smart Phones allow product variations, we even must
adopt the template for adding the product to the cart.


Use one of the demos as a starting point for your project
=========================================================

Depending on the needs of your e-commerce site, the easiest approach to start with **djangoSHOP**
is to use the demo which is most similar to one of the five from above. Then by copying example,
create a repository of the merchant's implementation. Starting from a working example and gradually
modifying it until reaching your final goals, typically is much easier than starting from scratch.
It also is the preferred way during agile development.


.. _Docker runtime environment: https://docs.docker.com/windows/
.. _django-parler: http://django-parler.readthedocs.org/en/latest/
.. _polymorphism: https://django-polymorphic.readthedocs.org/en/latest/
.. _slug:
.. _djangocms-cascade: http://djangocms-cascade.readthedocs.io/en/latest/
