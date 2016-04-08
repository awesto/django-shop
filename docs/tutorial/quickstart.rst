.. _tutorial/quickstart:

=========================
Quickstart a Running Demo
=========================

Using a Docker image
====================

To get a first impression of the **djangoSHOP** examples, you may use a prepared Docker container.
If not already available on your workstation, first install the `Docker runtime environment`_ and
start a Docker machine.

Now you may run a fully configured **djangoSHOP** image on your local machine:

.. code-block:: bash

	docker run -p 9001:9001 jrief/myshop-sample:latest

This image is rather large (1.9 GB) therefore it may take some time to download.

Locate the IP address of the running container using ``docker-machine ip default``. Then point
a browser onto this address using port 9001, for instance http://192.168.99.100:9001/en/

Please note that before bootstrapping, a full text index is built and the images are thumbnailed.
This takes additional time. Therefore, if you stop the running container, before rerunning the
Docker image it is recommended to restart the container. First locate it using

.. code-block:: bash

	$ docker ps -a
	CONTAINER ID  IMAGE                           COMMAND                 CREATED
	79b7b69a7473  jrief/myshop-sample:latest  "/usr/sbin/uwsgi --in"  11 minutes ago
	...
	$ docker start 79b7b69a7473

and then restart it. The access the administration backed, sign in as user "*admin*" with
password "*secret*".

.. note:: This demo does not function with the Payment Service Provider Stripe, because each
	merchant requires its own credentials. The same applies for sending emails, because
	the application requires an outgoing SMTP server.


The classic approach
====================

Alternatively you may also download all dependencies and start the project manually. If you want to
use the demo as a starting point, this probably is the better solution.

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

.. _download the media files: http://downloads.django-shop.org/django-shop-workdir.tar.gz
.. _django-parler: http://django-parler.readthedocs.org/en/latest/
.. _django-polymorphic: https://django-polymorphic.readthedocs.org/en/latest/


Simple Product Demo
===================

Assure you are in the ``django-shop`` folder and using the correct virtual environment. Then in a
shell invoke:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=simple DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-simple.json
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and sign in as user "*admin*" with password
"*secret*".

This runs the demo for :ref:`tutorial/simple-product`.


Internationalized Products
==========================

In this demo the description of the products can be translated into different natural languages.

When migrating from the Simple Products demo, assure you are in the ``django-shop`` folder and
using the correct virtual environment. Then in a shell invoke:

.. code-block:: shell

	(shoptutorial)$ cp workdir/db-simple.sqlite3 workdir/db-i18n.sqlite3
	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=i18n DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py runserver

Alternatively, if you prefer to start with an empty database, assure that the file
``workdir/db-i18n.sqlite3`` is missing. Then in a shell invoke:

.. code-block:: shell

	(shoptutorial)$ cd example
	(shoptutorial)$ export DJANGO_SHOP_TUTORIAL=i18n DJANGO_DEBUG=1
	(shoptutorial)$ ./manage.py migrate
	(shoptutorial)$ ./manage.py loaddata fixtures/myshop-i18n.json
	(shoptutorial)$ ./manage.py runserver

Point a browser onto http://localhost:8000/admin/ and sign in as user "*admin*" with password
"*secret*".

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

Point a browser onto http://localhost:8000/admin/ and sign in as user "*admin*" with password
"*secret*".

This runs a demo for :ref:`tutorial/polymorphic-product`.


.. _Docker runtime environment: https://docs.docker.com/windows/
