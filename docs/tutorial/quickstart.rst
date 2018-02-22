.. _tutorial/quickstart:

=======================
Quickstart using Docker
=======================

To get a first impression of the **django-SHOP** demos, please use the prepared Docker compose
file. If not already available on your workstation, first install the `Docker runtime environment`_
and start the local Docker machine.


.. _tutorial/prepared-docker-image:

Start with a prepared Docker Image
==================================

To run a set of configured **django-SHOP** containers on your local machine:

.. code-block:: bash

	$ git clone --depth 1 https://github.com/awesto/django-shop
	$ cd django-shop
	$ export DJANGO_SHOP_TUTORIAL=commodity
	$ docker-compose up --build -d

This will take a few minutes, so have a coffee. If everything is build, check if all containers are
up and running:

.. code-block:: bash

	$ docker ps
	CONTAINER ID   IMAGE                 COMMAND                  CREATED          STATUS          PORTS                              NAMES
	ddd453ae7eda   demoshop              "uwsgi --ini uwsgi..."   13 seconds ago   Up 12 seconds   0.0.0.0:9009->9009/tcp             djangoshop_wsgiapp_1
	7a39223ccd25   demoshop              "su django -c /web..."   13 seconds ago   Up 12 seconds                                      djangoshop_worker_1
	780c10e59831   elasticsearch:1.7.5   "/docker-entrypoin..."   15 seconds ago   Up 13 seconds   0.0.0.0:9200->9200/tcp, 9300/tcp   elasticsearch
	649ea9042252   redis                 "docker-entrypoint..."   15 seconds ago   Up 14 seconds   6379/tcp                           djangoshop_redishost_1
	7144f3e1a801   postgres              "docker-entrypoint..."   15 seconds ago   Up 14 seconds   5432/tcp                           djangoshop_postgresdb_1

The container ``djangoshop_wsgiapp_1`` is the actual webservice. Thanks to uWSGI_ it listens
for HTTP requests. This can be changed though, see below.

The container ``djangoshop_worker_1`` is based on the same image as ``djangoshop_wsgiapp_1``, and
its only purpose is to execute asynchronous tasks, such as delivering emails, indexing the search
engine and removing obsolete rows from the database.

The remaining three containers are based on their standard images as found on the Docker Hub:

* ``djangoshop_postgresdb_1`` provides the Postgres database.
* ``djangoshop_redishost_1`` provides a shared memory datastore with integrated message queue.
* ``elasticsearch`` provides fulltext index search engine.


Browse the demo
---------------

First locate the IP address of your Docker machine using ``docker-machine ip default``. Then point
a browser onto this address using port 9009, for instance http://192.168.99.100:9009/ (the IP
address may vary depending on your Docker machine settings) or http://localhost:9009/ if running on
Linux.

After the containers started, it may take a few minutes until the database is ready. The first time
a page is loaded, this also takes additional time because all images must be thumbnailed. The search
index will be available only after a few minutes. Note: Searching is not available for the simple
demos ``commodity`` and ``i18n_commodity``.


Stopping the containers
-----------------------

Stop and remove all containers by invoking:

.. code-block:: bash

	$ docker-compose down

All changes are persisted inside their Docker volumes. List them using:

.. code-block:: bash

	$ docker volume ls
	local     djangoshop_esdata
	local     djangoshop_pgdata
	local     djangoshop_redisdata
	local     djangoshop_shopmedia

To access the administration backed, navigate to http://192.168.99.100:9001/admin/ and sign
in as user "*admin*" with password "*secret*". If you navigate to any page of the shop, you may
switch into live edit mode and change the content of the various pages, including the product's
details pages.


Try out the other examples
--------------------------

By changing the environment variable ``DJANGO_SHOP_TUTORIAL`` to ``commodity``, ``i18n_commodity``,
``smartcard``, ``i18n_smartcard``, ``polymorphic`` or ``i18n_polymorphic``, you can examine one of
the other prepared examples. Afterwards re-create the container using the already built Docker images:

.. code-block:: bash

	$ export DJANGO_SHOP_TUTORIAL=i18n_commodity
	$ docker-compose up -d


Troubleshooting
---------------

If something doesn't work as expected, first check the logs, for instance as:

.. code-block:: bash

	$ docker container logs djangoshop_wsgiapp_1

To access a running Docker container, attach to it using:

.. code-block:: bash

	$ docker exec -ti djangoshop_wsgiapp_1 /bin/bash
	[root@example]# ps fax

If you don't have a running container, but want to examine the image's content, create a "throw-away"
container and access files through the shared volumes:

.. code-block:: bash

	$ docker run --rm -ti --volume djangoshop_shopmedia:/web/workdir demoshop /bin/bash
	[root@example]# ls -l /web/workdir

.. _Docker runtime environment: https://docs.docker.com/windows/
.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/


Configure an outgoing SMTP server
---------------------------------

In order to deliver emails to a real address, we must configure an outgoing SMTP-relay.
Please set these environment variables, or edit the file ``example/docker-files/email.environ`` and
configure the relay connection and their credentials using:

* DJANGO_EMAIL_HOST
* DJANGO_EMAIL_PORT
* DJANGO_EMAIL_USER
* DJANGO_EMAIL_PASSWORD
* DJANGO_EMAIL_USE_TLS
* DJANGO_EMAIL_FROM
* DJANGO_EMAIL_REPLY_TO


Now proceed with the next section, by :ref:`tutorial/add-pages-cms`.

