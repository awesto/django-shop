.. _reference/docker:

=======================
Deployment using Docker
=======================

By using Docker_ in combination with Docker Compose, the deployment of a **django-SHOP**
installation becomes really simple. We make use of this in the demos, but these examples
are intended to run on a local docker machine, hence there we use the internal web server
provided by uWSGI_. In a productive environment, we usually use a web server to dispatch
HTTP requests onto a backend application server. This setup has been tested with NGiNX_,
which allows us to dispatch multiple server names using the same IP address. Moreover, it
also terminates all https connections.


Get started with the django-SHOP container composition
======================================================

Each instance of a **django-SHOP** installation consists of at least 3 Docker containers. Some of
them, such as ``postgres``, ``redis`` and ``elasticsearch`` are build from the standard images as
provided by Docker-Hub. They do not require customized Docker files.

Only the one providing the merchant implementation must be built using a project specific
``Dockerfile``.

Before we start, let's create a folder named ``docker-files``. All files added to this folder shall
be managed by the version control system of your choice.


Configure uWSGI
---------------

Add a file named ``uwsgi.ini`` to the folder named ``docker-files``. This is the main configuration
file for our web application worker. uWSGI_ has incredibly many configuration options and can be
fine-tuned to your projects needs. Please consult their documentation for the given configuration
options.

.. code-block:: text
	:caption: docker-files/uwsgi.ini

	[uwsgi]
	chdir = /web
	umask = 002
	uid = django
	gid = django
	if-env = VIRTUAL_PROTO
	socket = :9009
	endif =
	if-not-env = VIRTUAL_PROTO
	http-socket = :9009
	endif =
	exec-pre-app = /web/manage.py migrate
	module = wsgi:application
	buffer-size = 32768
	static-map = /media=/web/workdir/media
	static-map = /static=/web/staticfiles
	static-expires = /* 7776000
	offload-threads = %k
	post-buffering = 1
	processes = 1
	threads = 1

Depending on whether ``VIRTUAL_PROTO`` is set to ``uwsgi`` (see below) or not, uWSGI either starts
as a socket server listening for WSGI requests, or as a pure web server listening for HTTP requests.
The latter is useful for testing the uWSGI application server, without having to run NGiNX as
frontend. For example, this setup is used by the tutorial.

The directive ``exec-pre-app`` performs a database migration whenever a new version of the built
containers is started. This means that we can only perform forward migrations, which is the usual
case anyway. In the rare occasion, when we have to perform a backward migration, we have to do that
manually by entering into the running container, using ``docker exec -ti containername /bin/bash``.

The directives ``static-map`` point onto the folders containing the collected static- and
media-files. These folders are referenced by the configuration directives ``STATIC_ROOT`` and
``MEDIA_ROOT`` in the projects ``settings.py``, so make sure they correspond to each other.

The directives ``processes`` and ``threads`` shall be adopted to the expected system load and
the machine's equipment.


Building the Images
-------------------

We need a recipe to build the image for two of the containers in our project: ``wsgiapp`` and
an optional ``worker``. The latter is a stand-alone Python script for :ref:`reference/worker`.
Since it runs in the same environment as our Django app, we use the same Docker image running
two different containers.

Add a file name ``Dockerfile`` to the folder named ``docker-files``.

.. code-block:: text
	:caption: docker-files/Dockerfile

	FROM python:3.5
	ENV PYTHONUNBUFFERED 1
	RUN mkdir /web
	WORKDIR /web
	ARG DJANGO_MEDIA_ROOT=/web/workdir/media
	ARG DJANGO_STATIC_ROOT=/web/staticfiles

	# other additional packages outside of PyPI
	RUN apt-get update
	RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
	RUN apt-get install -y nodejs gdal-bin
	RUN rm -rf /var/lib/apt/lists/*

	# install project specifiy requirements
	ADD requirements /tmp/requirements
	RUN pip install -r /tmp/requirements/version-0.5.txt
	RUN pip install 'uWSGI<2.1'
	RUN groupadd -g 1000 django
	RUN useradd -M -d /web -u 1000 -g 1000 -s /bin/bash django

	# copy project relevant files into container
	ADD my_shop /web/my_shop
	ADD package.json /web/package.json
	ADD package-lock.json /web/package-lock.json
	ADD manage.py /web/manage.py
	ADD wsgi.py /web/wsgi.py
	ADD worker.py /web/worker.py
	ADD docker-image/uwsgi.ini /web/uwsgi.ini
	RUN npm install

	# handle static files
	ENV DJANGO_STATIC_ROOT=$DJANGO_STATIC_ROOT
	RUN mkdir -p $DJANGO_STATIC_ROOT/CACHE
	RUN _BOOTSTRAPPING=1 ./manage.py compilescss
	RUN _BOOTSTRAPPING=1 ./manage.py collectstatic --noinput --ignore='*.scss'
	RUN chown -R django.django $DJANGO_STATIC_ROOT/CACHE

	# handle media files in external volume
	ENV DJANGO_MEDIA_ROOT=$DJANGO_MEDIA_ROOT
	RUN mkdir -p $DJANGO_MEDIA_ROOT
	RUN chown -R django.django $DJANGO_MEDIA_ROOT

	EXPOSE 9009
	VOLUME /web/workdir

A container of this Docker image runs both, the Django application server and the asynchronous
worker. Please refer to the Docker documentation for details on the applied directives.

Ensure that the media directory is located inside a Docker volume. Otherwise all uploaded media
files are lost, whenever the image is rebuilt.

The port, on which the application server is listening for connections, must be exposed by Docker.
Therefore ensure that the setting ``EXPOSE`` matches with the settings for ``socket``/``http-socket``
used by the uWSGI daemon in ``uwsgi.ini`` (see above).


Environment Variables
---------------------

Some images must communicate with each other and hence require common configuration settings. In
order not having to repeatedly typing them, we use a common configuration file used by more than one
Docker image configuration. There we store our environment variables used for our configuration.

Add a file name ``environ`` to the folder named ``docker-files``.

.. code-block:: text
	:caption: docker-files/environ

	POSTGRES_DB=my_pg_database
	POSTGRES_USER=my_pg_user
	POSTGRES_PASSWORD=my_pg_passwd
	POSTGRES_HOST=postgresdb
	REDIS_HOST=redishost
	ELASTICSEARCH_HOST=elasticsearch
	DJANGO_EMAIL_HOST=outgoing_smtp_server
	DJANGO_EMAIL_PORT=587
	DJANGO_EMAIL_USER=email_user
	DJANGO_EMAIL_PASSWORD=email_password
	DJANGO_EMAIL_USE_TLS=yes
	DJANGO_EMAIL_FROM=no-reply@example.com
	DJANGO_EMAIL_REPLY_TO=info@example.com

Replace the values of these environment variables with whatever is appropriate for your setup.


Composing everything together
-----------------------------

The final step is to compose everything together, so that every service runs in its own container.
This is the way Docker is intended to be used. For this we require a file named
``docker-compose.yml``. This file must be placed at the root of the merchant's project:

.. code-block:: yaml
	:caption: docker-compose.yml

	version: '2.0'

	services:
	  postgresdb:
	    restart: always
	    image: postgres
	    env_file:
	      - docker-files/environ
	    volumes:
	      - pgdata:/var/lib/postgresql/data
	    networks:
	      - shopnet

	  redishost:
	    image: redis
	    volumes:
	      - 'redisdata:/data'
	    networks:
	      - shopnet

	  elasticsearch:
	    image: elasticsearch:1.7.5
	    container_name: elasticsearch
	    environment:
	      - cluster.name=docker-cluster
	      - bootstrap.memory_lock=true
	      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
	    ulimits:
	      memlock:
	        soft: -1
	        hard: -1
	    volumes:
	      - esdata:/usr/share/elasticsearch/data
	    networks:
	      - shopnet

	  wsgiapp:
	    restart: always
	    build:
	      context: .
	      dockerfile: docker-files/Dockerfile
	    image: my_shop
	    env_file:
	      - docker-files/environ
	    volumes:
	      - shopmedia:/web/workdir/media
	    command: uwsgi --ini uwsgi.ini
	    depends_on:
	      - postgresdb
	      - redishost
	      - elasticsearch
	    networks:
	      - shopnet
	    ports:
	      - 9009:9009

	  worker:
	    restart: always
	    image: my_shop
	    env_file:
	      - docker-files/environ
	    command: su django -c /web/worker.py
	    volumes:
	      - shopmedia:/web/workdir/media
	    depends_on:
	      - postgresdb
	      - redishost
	    networks:
	      - shopnet

	networks:
	  shopnet:

	volumes:
	  pgdata:
	  redisdata:
	  shopmedia:
	  esdata:


Before proceeding with the final setup, we try to build and start a stand-alone version of this web
application. This helps to find errors much quicker, in case something went wrong.

.. code-block:: bash

	$ docker-compose up --build

This step will take a while, especially the first time, since many Docker images must be downloaded
from the Docker hub. If all containers are up and running, point a browser onto the IP address of
the docker-machine and on port 9009. The IP address can be discovered by invoking
``docker-machine ip``.

If everything works, we stop the containers using ``CTRL-C`` and proceed to the next section.
In case a problem occurred, check the log statements dumped onto the terminal.


Run NGiNX with Let's Encrypt
============================

In a production environment, usually you run these, and probably other containers behind a single
NGiNX instance. Additionally, since our customers normally do provide their user credentials and
other sensitive information, such as credit card numbers, we *must* ensure that our connection is
secured by https.

To do so, we run a separate composition of two Docker containers using this configuration in a
file named ``nginx-compose.yml``.

.. code-block:: yaml
	:caption: nginx-compose.yml

	version: '2.0'

	services:
	  nginx-proxy:
	    restart: always
	    image: jwilder/nginx-proxy:latest
	    ports:
	      - '80:80'
	      - '443:443'
	    volumes:
	      - '/var/run/docker.sock:/tmp/docker.sock:ro'
	      - '/etc/nginx/vhost.d'
	      - '/usr/share/nginx/html'
	      - '/etc/nginx/certs'
	    networks:
	      - nginx-proxy

	  letsencrypt-nginx-proxy-companion:
	    image: jrcs/letsencrypt-nginx-proxy-companion
	    volumes:
	      - '/var/run/docker.sock:/var/run/docker.sock:ro'
	    volumes_from:
	      - 'nginx-proxy'

	networks:
	  nginx-proxy:
	    external: true

If we build these containers the first time, we might have to create the network, since it is
declared as external:

.. code-block:: bash

	$ docker network create nginx-proxy

To build and run the web server plus Let's Encrypt companion, we invoke:

.. code-block:: bash

	$ docker-compose -f nginx-compose.yml up --build -d

This spawns up two running Docker containers, where ``nginx-proxy`` is the actual webserver and
``letsencrypt-nginx-proxy-companion`` just manages the SSL certificates using the `Let's Encrypt`_
certification authority. Note that you must point at least one DNS entry onto the IP address of
this host. This name must resolve by the global Domain Name Service.

Check if everything is up and running:

.. code-block:: bash

	$ docker-compose -f nginx-compose.yml ps
	                     Name                                   Command               State                   Ports
	------------------------------------------------------------------------------------------------------------------------------------
	nginxproxy_letsencrypt-nginx-proxy-companion_1   /bin/bash /app/entrypoint. ...   Up
	nginxproxy_nginx-proxy_1                         /app/docker-entrypoint.sh  ...   Up      10.9.8.7:443->443/tcp, 10.9.8.7:80->80/tcp

Pointing a browser onto the IP address of our docker-machine will raise a Gateway error. This is
intended behaviour, because our NGiNX yet does not know where to route incoming requests.


Provide django-SHOP behind NGiNX
--------------------------------

Finally we want to run our **django-SHOP** instance behind the just configured NGiNX proxy.
For this we have to edit the file ``docker-compose.yml`` from above. There we change to following
lines:

* In section ``wsgiapp``, add the environment variables ``VIRTUAL_HOST``, ``VIRTUAL_PROTO``,
  ``LETSENCRYPT_HOST`` and ``LETSENCRYPT_EMAIL`` to subsection ``environment``, as shown below.
  They are used to configure the NGiNX-Proxy.
* In section ``wsgiapp``, add ``nginx-proxy`` to subsection ``networks`` and to the global
  section ``networks``, as shown below.
* Since we don't need to access our WSGI application via an externally reachable port, we can
  remove the ``ports`` configuration from section ``wsgiapp``.

.. code-block:: yaml
	:caption: docker-compose.yml

	  wsgiapp:
	    ...
	    environment:
	      - VIRTUAL_HOST=www.my_shop.com
	      - VIRTUAL_PROTO=uwsgi
	      - LETSENCRYPT_HOST=www.my_shop.com
	      - LETSENCRYPT_EMAIL=ssladmin@my_shop.com
	    ...
	    networks:
	      - shopnet
	      - nginx-proxy
	  ...
	  networks:
	    shopnet
	    nginx-proxy:
	      external: true

Re-create and run the Docker containers using:

.. code-block:: bash

	$ docker-compose up --build -d

The container ``wsgiapp`` then starts to communicate with the container ``nginx-proxy`` and
reconfigures its virtual hosts settings without requiring any other intervention. The same also
applies for the container ``letsencrypt-nginx-proxy-companion``, which then issues a certificate
from the Let's Encrypt Certification Authority. This may take a few minutes.

To check if everything is up and running, invoke:

.. code-block:: bash

	$ docker-compose ps
	        Name                         Command               State    Ports
	-------------------------------------------------------------------------------------
	my_shop_elasticsearch_1   /docker-entrypoint.sh elas ...   Up      9200/tcp, 9300/tcp
	my_shop_postgresdb_1      docker-entrypoint.sh postgres    Up      5432/tcp
	my_shop_redishost_1       docker-entrypoint.sh redis ...   Up      6379/tcp
	my_shop_webapp_1          uwsgi --ini uwsgi.ini            Up      9007/tcp
	my_shop_worker_1          su django -c /web/worker.py      Up      9007/tcp


Troubleshooting
===============

If anything goes wrong, a good place to start is to check the logs. Accessing the logs is as easy as
invoking:

	$ docker container logs my_shop_webapp_1

.. _Docker: https://docs.docker.com/get-started/
.. _uWSGI: http://uwsgi.readthedocs.org/
.. _Let's Encrypt: https://letsencrypt.org/
.. _NGiNX: https://www.nginx.com/
