.. _tutorial/quickstart:

======================
Qucikstart with Docker
======================

To get a first impression of the **django-SHOP** demos, please use one of the prepared Docker
images. If not already available on your workstation, first install the
`Docker runtime environment`_ and start the local Docker machine.


.. _tutorial/prepared-docker-image:

Start with a prepared Docker Image
==================================

To run a fully configured **django-SHOP** container on your local machine:

.. code-block:: bash

	docker run --name demo-shop-i18n_polymorphic --env DJANGO_SHOP_TUTORIAL=i18n_polymorphic -p 9001:9001 awesto/demo-shop:latest

This image is rather large (~2 GB), therefore it may take some time to download.

Locate the IP address of the running container using ``docker-machine ip default``. Then point
a browser onto this address using port 9001, for instance http://192.168.99.100:9001/

After the container started, it may take a few minutes until the database is ready. The first time
a page is loaded, also takes additional time because all images must be thumbnailed. Therefore, if
you stop the running container with

.. code-block:: bash

	docker stop demo-shop-i18n_polymorphic

instead of re-running the supplied Docker image, it is recommended to restart the just created
container with:

.. code-block:: bash

	$ docker start demo-shop-i18n_polymorphic

To access the administration backed, navigate to http://192.168.99.100:9001/admin/ and sign
in as user "*admin*" with password "*secret*". If you navigate to any page of the shop, you may
switch into live edit mode and change the content of the various pages, including the product's
details pages.


Try out the other examples
--------------------------

By changing the environment variable ``DJANGO_SHOP_TUTORIAL`` to ``commodity``, ``i18n_commodity``,
``smartcard``, ``i18n_smartcard``, ``polymorphic`` or ``i18n_polymorphic``, you can examine one of
the other prepared examples. Afterwards re-create the container using the same Docker image:

.. code-block:: bash

	docker run --name demo-shop-commodity --env DJANGO_SHOP_TUTORIAL=commodity -p 9001:9001 awesto/demo-shop:latest


Troubleshooting
---------------

To access a running Docker container from outside, attach to it using:

.. code-block:: bash

	docker exec -ti demo-shop-i18n_polymorphic /bin/bash
	[root@example]# ps fax

If you don't want to interfere with the running container, you may create a "throw-away" container
and access files through the shared volume named ``/web``. Here you can read the logs and change
some basic settings. If you modify the timestamp of ``/web/workdir/myshop.ini`` **uWSGI** restarts
the Django server. To access this shared volume, start a throw away container with:

.. code-block:: bash

	docker run --rm -ti --volumes-from demo-shop-commodity demo-shop /bin/bash
	[root@example]# cd /web/logs
	[root@example]# less shop.log

.. _Docker runtime environment: https://docs.docker.com/windows/
