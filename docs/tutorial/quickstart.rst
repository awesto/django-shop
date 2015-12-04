=========================
Start with a running demo
=========================

Filling your CMS with page content and adding products is a boring job. Therefore you can start the
three demos with some prepared sample data. First download some media data from:


Assure that a virtual environment is installed as described in the :ref:`intro` section.


Install django-shop
===================

.. code-block:: shell

	$ virtualenv shoptutorial
	$ source shoptutorial/bin/activate
	(shoptutorial)$ git clone https://github.com/jrief/django-shop
	(shoptutorial)$ cd django-shop
	(shoptutorial)$ pip install -r requirements/common.txt
	(shoptutorial)$ pip install -e .
	(shoptutorial)$ tar zxf DOWNLOAD/FOLDER/django-shop-sample-media.tar.gz

Starting from this folder, you can run all three demos. The unpatient user can skip the first two
demos; each of them can be started on its own.


Simple Product
==============

Assure you are in the ``django-shop`` folder and using the correct virtual environment.

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=simple
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-simple.json
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and log in as ``admin`` with password ``secret``.

This runs a demo for :ref:`simple-product`.


Internationalized Products
==========================

In this demo the description of the products can be translated into different natural languages.

When migrating from the Simple Products demo, assure you are in the ``django-shop`` folder and
using the correct virtual environment:

.. code-block:: shell

	(shoptutorial)$ cp workdir/db-simple.sqlite3 workdir/db-i18n.sqlite3
	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=i18n
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py runserver

Alternatively, if you prefer to starting with an empty database, assure that the file
``workdir/db-i18n.sqlite3`` is missing:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=i18n
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-i18n.json
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and log in as ``admin`` with password ``secret``.

This runs a demo for :ref:`multilingual-product`.


Polymorphic Products
====================

In this demo we show how to handle products with different types in different natural languages.

When migrating from the Internationalized Products demo, assure you are in the ``django-shop``
folder and using the correct virtual environment:

.. code-block:: shell

	(shoptutorial)$ cp workdir/db-i18n.sqlite3 workdir/db-polymorphic.sqlite3
	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=polymorphic
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py runserver

This will allow you to add Smart Phones in addition to the existing Smart Cards. Since you probably
want to experiment with some prepared Smart Phones, restart with a fixture which already contains
them:

.. code-block:: shell

	(shoptutorial)$ rm workdir/db-polymorphic.sqlite3
	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=polymorphic
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-polymorphic.json
	(shoptutorial)$ ./manage.py runserver

