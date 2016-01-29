.. _tutorial/quickstart:

=========================
Quickstart a Running Demo
=========================

Filling your CMS with page content and adding products is a boring job. Impatient users may start
three demos using some prepared sample data. First assure that all dependencies are installed
into its virtual environment as described in section ":ref:`tutorial/prepare-installation`". Then
instead of adding pages and products manually, `download the media files`_ and unpack them into the
folder ``django-shop``:

.. code-block:: shell

	(shoptutorial)$ tar zxf DOWNLOAD/FOLDER/django-shop-workdir.tar.gz

Starting from this folder, you can run all three demos: The first, simple demo shows how to setup a
monolingual shop, with one product type. The second, internationalized demo shows how to setup a
multilingual shop, with one product type. For translation of model attributes, this installation
uses the django-parler_ app. The third, polymorphic demo shows how to setup a shop with many
different product types. To handle the polymorphism of products, this installation uses the
django-polymorphic_ app.

.. note:: All demos can be started independently from each other, but you are encouraged to start
		with the "Simple Product", and then proceed to the more complicate examples.

.. _download the media files: http://downloads.awesto.com/django-shop-workdir.tar.gz
.. _django-parler: http://django-parler.readthedocs.org/en/latest/
.. _django-polymorphic: https://django-polymorphic.readthedocs.org/en/latest/


Simple Product Demo
===================

Assure you are in the ``django-shop`` folder and using the correct virtual environment. Then in a
shell invoke:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=simple
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-simple.json
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and log in as ``admin`` with password ``secret``.

This runs the demo for :ref:`tutorial/simple-product`.


Internationalized Products
==========================

In this demo the description of the products can be translated into different natural languages.

When migrating from the Simple Products demo, assure you are in the ``django-shop`` folder and
using the correct virtual environment. Then in a shell invoke:

.. code-block:: shell

	(shoptutorial)$ cp workdir/db-simple.sqlite3 workdir/db-i18n.sqlite3
	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=i18n
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py runserver

Alternatively, if you prefer to start with an empty database, assure that the file
``workdir/db-i18n.sqlite3`` is missing. Then in a shell invoke:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=i18n
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-i18n.json
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and log in as ``admin`` with password ``secret``.

This runs a demo for :ref:`tutorial/multilingual-product`.


Polymorphic Products
====================

In this demo we show how to handle products with different properties and in different natural
languages. This example can't be migrated from the previous demos, without loosing lots of
information. It is likely that you don't want to add the Smart Phones manually, it is suggested
to start using a fixture.

This example shows how to add Smart Phones in addition to the existing Smart Cards. Assure you are
in the ``django-shop`` folder and using the correct virtual environment. Then in a shell invoke:

.. code-block:: shell

	(shoptutorial)$ rm workdir/db-polymorphic.sqlite3
	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=polymorphic
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-polymorphic.json
	(shoptutorial)$ ./manage.py runserver

This runs a demo for :ref:`tutorial/polymorphic-product`.
