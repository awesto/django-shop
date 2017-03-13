.. _tutorial/quickstart:

=========================
Quickstart a Running Demo
=========================

Using a Docker image
====================

To get a first impression of the **django-SHOP** demos, please use one of the prepared Docker
images. If not already available on your workstation, first install the
`Docker runtime environment`_ and start a Docker machine.

To run a fully configured **django-SHOP** image on your local machine:

.. code-block:: bash

	docker run -p 9001:9001 --name demo-shop-polymorphic-initial awesto/demo-shop-polymorphic:latest

This image is rather large (~2 GB), therefore it may take some time to download.

Locate the IP address of the running container using ``docker-machine ip default``. Then point
a browser onto this address using port 9001, for instance http://192.168.99.100:9001/en/

Please note that before the server starts, a full-text index is built and the images are
thumbnailed; this takes some additional time. Therefore, if you stop the running container with

.. code-block:: bash

	docker stop demo-shop-polymorphic-initial

instead of re-running the supplied Docker image, it is recommended to restart the just created
container with

.. code-block:: bash

	$ docker start demo-shop-polymorphic-initial

To access the administration backed, navigate to http://192.168.99.100:9001/en/admin/ and sign
in as user "*admin*" with password "*secret*". If you now navigate to any page of the shop, you may
switch into live edit mode and change the content of the various pages, including the product's
details pages.


Running Demos Locally
=====================

You may download all dependencies and start the testing projects manually. If you want to use the
demo as a starting point for your own project, then this presumably is the better solution.

Filling your CMS with page content and adding products is a boring job. Impatient users can start
with one of the five provided demos, using prepared sample data. First assure that all dependencies
are installed into its virtual environment as described in section :ref:`tutorial/prepare-installation`.
Then instead of adding pages and products manually, use the following steps:

.. code-block:: shell

	(shoptutorial)$ cd django-shop/example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=commodity DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py initialize_shop_demo
	(shoptutorial)$ ./manage.py compilescss
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and sign in as user *admin* with password
*secret*.

This runs the demo for :ref:`tutorial/commodity`.

.. note:: The first time, **django-SHOP** renders a page, images must be thumbnailed and cropped.
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
**django-SHOP** framework. It is intended for shops where the merchant does not want to create a
customized product model, but rather prefers to create the product's detail views using common CMS
functionality.

A **Commodity** model contains only the following attributes:

* The name of the product.
* The product code.
* The slug_ (a short label used as the last bit in the URLs).
* The product's unit price.
* One sample image to be shown in the catalog's list view.
* A caption to be shown in the catalog's list view.

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

* The name of the product.
* The slug.
* A caption to be shown in the catalog's list view.

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
don't require a translatable field for the product name and its slug.


The Polymorphic Product Model
-----------------------------

The ``polymorphic`` demo is a combination from all of the examples from above. Here we declare a
base product model using the class :class:`myshop.models.polymorphic_.Product`. We also declare
common fields available in all of our different product types. These fields act as the smallest
common denominator for the views where we want to display summary information about our products,
independently of their characteristics.

List views showing a summary information about our products are the *Cart View*, the *Order Detail
View* and eventually the *Catalog List View*.

The model classes for Smart Card, Smart Phone and a variation of Commodity then inherit from this
base product class. These models additionally can declare attributes required to describe the
physical properties of each product type. Since they vary, we also have to create special templates
for the detail views of each of them. Since Smart Phones allow product variations, we even must
adopt the template for adding the product to the cart.


The Internationalized Polymorphic Product Model
-----------------------------------------------

The ``i18n_polymorphic`` demo is a variation of the above example, with a few attributes translated
into multiple languages, namely ``caption`` and ``description``. This sample implementation does not
use translated slugs, although this would be possible.


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
sample. Having a working implementation you may gradually modifying it until reaching your final
goal. Typically this approach is much easier than starting from scratch and also is the preferred
way during agile development.


.. _Docker runtime environment: https://docs.docker.com/windows/
.. _django-parler: http://django-parler.readthedocs.org/en/latest/
.. _polymorphism: https://django-polymorphic.readthedocs.org/en/latest/
.. _slug: https://docs.djangoproject.com/en/stable/glossary/#glossary
.. _djangocms-cascade: http://djangocms-cascade.readthedocs.io/en/latest/
