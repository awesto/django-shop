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
a browser onto this address using port 9001, for instance http://192.168.99.100:9001/ (the IP
address may vary depending on your Docker machine settings).

After the container started, it may take a few minutes until the database is ready. The first time
a page is loaded, this also takes additional time because all images must be thumbnailed. Therefore,
if you stop the running container with

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
``smartcard``, ``i18n_smartcard`` or ``polymorphic``, you can examine one of the other prepared
examples. Afterwards re-create the container using the same Docker image:

.. code-block:: bash

	docker run --name demo-shop-commodity --env DJANGO_SHOP_TUTORIAL=commodity -p 9001:9001 awesto/demo-shop:latest


Troubleshooting
---------------

Running Docker containers can not be accessed from outside, therefore it is very difficult to look
at their internals. To allow customers to read the logs and change some basic settings, this
container keeps all non-reproducible data in a separate volume named ``/web``, which can be
mounted externally. To access this volume, start a throw away container with:

```
docker run --rm -ti --volumes-from demo-shop-commodity demo-shop /bin/bash
[root@example]# ll /web/logs
[root@example]# less shop.log
```

.. _Docker runtime environment: https://docs.docker.com/windows/
