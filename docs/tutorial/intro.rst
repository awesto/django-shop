.. _tutorial/intro:

====================
Django-SHOP Tutorial
====================

This tutorial is aimed at people new to django-SHOP but already familiar with Django. If you aren't
yet, reading their excellent `Django Tutorial`_ is highly recommended.

Since **django-SHOP** relies on many features offered by `django-CMS`_ and `Django REST Framework`_,
you should familiarize yourself with these apps.

.. _django-CMS: https://django-cms.readthedocs.io/en/latest/
.. _Django REST Framework: https://www.django-rest-framework.org/


Introduction
============

**Django-SHOP** is an e-commerce framework rather than a turn-key solution. This means that the
merchant is in charge of the project and that **django-SHOP** acts as one of the third party
dependencies making up the whole project. We name this the *merchant implementation*.

The merchant implementation contains everything which makes up its fully customizable project,
such as:

* The main configuration file, ``settings.py``.
* The URL-routing entry point, usually ``urls.py``.
* Optionally, but highly recommended: Django models to describe the products sold by the merchant.
* If required, extended models for the Cart and Order.
* An administration interface to manage entities from all those models.
* Special Cart modifiers to calculate discounts or additional costs.
* Order workflows to handle all the steps how an order is processed.
* Apphooks for integrating Django-Views into **django-CMS**.
* Custom filters to restrict the rendered set of products according to their properties.
* Form definitions, if they differ from the built-in defaults.
* HTML snippets and their cascading style sheets, if they differ from the built-in defaults.

This approach allows a merchant to implement every desired extra feature, without having to
modify any code in the **django-SHOP** framework itself. This however requires to add some
custom code to the merchant implementation itself. Since we don't want to do this from scratch,
we can use a prepared `cookiecutter template`_ to bootstrap our first project. Please follow their
instructions for setting up a running demo.

This cookiecutter template is shipped with 3 distinct product models, which are named *commodity*,
*smartcard* and *polymorphic*. Depending on their need for internationalization, they are
subdivided into a variant for a single language and one with support for translated product
properties. Which one of them to use, depends on the merchant requirements. When answering the
questions, asked by the cookiecutter wizard, consider to:

* use *commodity*, if you want to fill a free-form page with components from the CMS. It does not
  require any adaption of the product model. It is useful for shops with a handful of different
  products. :ref:`tutorial/product-model-commodity` and :ref:`tutorial/product-model-i18n_commodity`
* use *smartcard*, if you have many products, which all share the same properties. It is useful for
  shops with one distinct product type. Here the product model usually must be renamed, and further
  adopted, by adding and removing fields. :ref:`tutorial/product-model-smartcard` and
  :ref:`tutorial/product-model-i18n_smartcard`
* use *polymorphic*, if you have many product types, with different properties for each type. Here
  we have to define a smallest common denominator for all products, and further create a product
  model for each distinct product type. :ref:`tutorial/product-model-polymorphic` and
  :ref:`tutorial/product-model-i18n_polymorphic`


.. _tutorial/installation:

Installation
============

Before installing the files from the project, ensure that your operating system contains these
applications:

* NodeJS_ including npm_.
* Python_ including pip_.

Install some additional Python applications, globally or for the current user:

.. code-block:: shell

	pip install --user pipenv cookiecutter autopep8

Then change into a directory, usually used for your projects and invoke:

.. code-block:: shell

	cookiecutter https://github.com/awesto/cookiecutter-django-shop

You will be asked a few question. If unsure, just use the defaults. This creates a directory named
``my-shop``, or whatever you have chosen. This generated directory is the base for adopting this
project into your *merchant implementation*. For simplicity, in this tutorial, it is referred as
``my-shop``. Change into this directory and install the missing dependencies:

.. code-block:: shell

	cd my-shop
	pipenv install --sequential
	npm install

This demo shop must initialize its database and be filled with content for demonstration purpose.
Each of these steps can be performed individually, but for simplicity we use a Django management
command which wraps all these command into a single one:

.. code-block:: shell

	pipenv run ./manage.py initialize_shop_demo

Finally we start the project, using Django's built-in development server:

.. code-block:: shell

	export DJANGO_DEBUG=1
	pipenv run ./manage.py runserver

Point a browser onto http://localhost:8000/ and check if everything is working. To access the
backend at http://localhost:8000/admin/ , log in using username *admin* with password *secret*.

.. note::
	The first time, **django-SHOP** renders a page, images must be thumbnailed and cropped.
	This is an expensive operation which runs only once. Therefore please be patient, when loading
	a page for the first time.


Overview
========

What you see here is a content management system consisting of many pages. By accessing the Django
administration backend at **Home › django CMS › Pages**, one gets an overview of the page-tree
structure. One thing which immediately stands out is, that all pages required to build the shop,
are actually pages, served by **django-CMS**. This means that the complete sitemap (URL structure)
of a shop, can be reconfigured easily to the merchants needs.


.. _tutorial/add-pages-cms:

Adding pages to the CMS
=======================

If we want to add pages to the CMS which have not been installed with the demo, we must sign in as
a Django staff user. If our demo has been loaded through one of the prepared fixtures, use user
*admin* with password *secret*. After signing in, a small arrow appears on the top right in our
browser. Clicking on that arrow expands the Django-CMS toolbar.

|django-cms-toolbar|

.. |django-cms-toolbar| image:: /_static/tutorial/django-cms-toolbar.png

Click on the menu item named **example.com** and select **Pages ...**. This opens the Django-CMS
*Page Tree*.  In **django-SHOP**, every page, can be rendered by the CMS. Therefore, unless we
need a special landing page, we can start immediately with the *Catalog's List View* of our
products.

Click on **New Page** to create a new Page. As its **Title** choose whatever seems appropriate.
Then change into the **Advanced Settings** at the bottom of the page. In this editor window,
locate the field **Template** and choose the default.

Change into **Structure** mode and locate the placeholder named **Main Content**, add a
**Container**-plugin, followed by a **Row**-, followed by one or more **Column**-plugins. Choose
the appropriate width for each column, so that for any given breakpoint, the widths units sum up
to 12. Below that column, add whatever is appropriate for that page. This is how in **django-CMS**
we add components to our page placeholders.

The default template provided with the demo contains other placeholders. One shall be used to
render the breadcrumb. By default, if no **Breadcrumb**-plugin has been selected, it shows the path
to the current page. By clicking on the ancestors, one can navigate backwards in the page-tree
hierarchy.


Next Chapter
============

In the next chapter of this tutorial, we will see how to organize the :ref:`tutorial/catalog-views`

.. _Django Tutorial: https://docs.djangoproject.com/en/stable/intro/tutorial01/
.. _cookiecutter template: https://github.com/awesto/cookiecutter-django-shop
.. _NodeJS: https://nodejs.org/en/
.. _npm: https://www.npmjs.com/get-npm
.. _Python: https://www.python.org/downloads/release/python-368/
.. _pip: https://pip.pypa.io/en/stable/installing/
