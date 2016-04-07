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
the pip-installable from PyPI only contains the main files. Before proceeding, please make sure
virtualenv_ is installed on your system, otherwise you would pollute your Python site-packages
folder.

Also ensure that these packages are installed using the favorite package manager of your operating
system:

* Python 2.7
* Redis: http://redis.io/
* SQLite: https://www.sqlite.org/
* bower: http://bower.io/
* Node Package Manager: https://www.npmjs.com/
* Python 2.7 (Latest minor version recommended)
* Django 1.9 (Latest minor version recommended)

.. code-block:: shell

	$ virtualenv shoptutorial
	$ source shoptutorial/bin/activate
	$ mkdir Tutorial; cd Tutorial
	(shoptutorial)$ git clone --depth 1 https://github.com/awesto/django-shop
	(shoptutorial)$ cd django-shop
	(shoptutorial)$ pip install -e .
	(shoptutorial)$ pip install -r requirements/tutorial.txt
	(shoptutorial)$ npm install
	(shoptutorial)$ bower install

these statements will setup an environment, which runs a demo shop out of the box.

You may populate the database with your own products, or if impatient, :ref:`tutorial/quickstart`
using prepared CMS page layouts, products and media files.


.. _tutorial/create-demo-database:

Create a database for the demo
------------------------------

Finally we must create a database to run our example project:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_DEBUG=1
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

In **djangoSHOP**, every page, with the exception of the product's detail pages, can be rendered by
the CMS. Therefore, unless you need a special landing page, start immediately with the *Catalog List
View* of your products. Change into the Django Admin backend, chose the section

**Start > django CMS > Pages**

and add a Page. As its **Title** chose “Smart Cards”. Then change into the **Advanced Settings**
at the bottom of the page. In this editor window, locate the field **Application** and select
**Products List**. Then save the page and click on **View on site**.

Now change into **Structure** mode and locate the placeholder named **Main content container**.
Add a plugin from section **Bootstrap** named **Row**. Below that Row add a Column with a width of
12 units. Finally, below the last Column add a plugin from section **Shop** named **Catalog List
View**.

Now we have a working catalog list view, but since we havn't added any products to the database
yet, we won't see any items on our page.


.. _Django Tutorial: https://docs.djangoproject.com/en/stable/intro/tutorial01/
