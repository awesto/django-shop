.. _tutorial/intro:

========
Tutorial
========

Introduction
============

This tutorial is aimed at people new to django SHOP but already familiar with Django. If you aren't
yet, reading their excellent `Django Tutorial`_ is highly recommended.

The steps outlined in this tutorial are meant to be followed in order.


.. _tutorial/prepare-installation:

Prepare the Installation
========================

To run the examples shown in this tutorial, you must install **django-shop** from GitHub, since
the pip-installable from PyPI only contains the framework but not the files required for the demos.
Before proceeding, please make sure virtualenv_ is installed on your system, otherwise you would
pollute your Python site-packages folder.

Also ensure that these packages are installed using the favorite package manager of your operating
system:

* Python 2.7 or 3.4 and later
* Redis: http://redis.io/
* SQLite: https://www.sqlite.org/
* Node Package Manager: https://www.npmjs.com/
* Python 2.7 or 3.4 and later

.. code-block:: shell

	$ virtualenv shoptutorial
	$ source shoptutorial/bin/activate
	$ mkdir Tutorial; cd Tutorial
	(shoptutorial)$ git clone --depth 1 https://github.com/awesto/django-shop
	(shoptutorial)$ cd django-shop
	(shoptutorial)$ pip install -r requirements/common.txt
	(shoptutorial)$ pip install --no-deps -e .
	(shoptutorial)$ pip install Django==1.10.5
	(shoptutorial)$ npm install

These statements will setup an environment that runs one of the demo shops out of the box.

.. note:: We recommend that you use Python 3, but if you stuck with Python-2.7, please note that
	you have to replace ``requirements/common.txt`` with ``requirements/py2.txt``.

If you want to populate the database with your own categories, products and pages, proceed as
described below. Otherwise, or if impatient, you may :ref:`tutorial/quickstart` using prepared
CMS page layouts, products and media files.


.. _tutorial/create-demo-database:

Create a database for the demo
------------------------------

Finally we must create a database to run our example project:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=commodity DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py createsuperuser
	Email address: admin@example.org
	Username: admin
	Password:
	Password (again):
	Superuser created successfully.
	(shoptutorial)$ ./manage.py runserver

Finally point a browser onto http://localhost:8000/ and log in as the superuser you just created.

.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/


Add some pages to the CMS
=========================

In **django-SHOP**, every page, can be rendered by the CMS. Therefore, unless you need a special
landing page, start immediately with the *Catalog's List View* of your products. Change into the
Django Admin backend, choose the section

**Start > django CMS > Pages**

and add a Page. As its **Title** choose “Smart Cards”. Then change into the **Advanced Settings**
at the bottom of the page. In this editor window, locate the field **Application** and select
**Products List**. Then save the page and click on **View on site**.

Now change into **Structure** mode and locate the placeholder named **Main Content**.
Add a plugin from section **Bootstrap** named **Row**. Below that Row add a Column with a width of
12 units. Finally, below the last Column add a plugin from section **Shop** named **Catalog List
View**.

Now we have a working catalog list view, but since we havn't added any products to the database
yet, we won't see any items on our page.


.. _Django Tutorial: https://docs.djangoproject.com/en/stable/intro/tutorial01/
