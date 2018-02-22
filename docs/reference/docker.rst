=======================
Deployment using Docker
=======================

By using Docker_ in combination with docker-compose_, the deployment of a **django-SHOP**
installation becomes really simple. We make use of this in the demos, but these examples
are intended to run on a local host, hence we can use the internal webserver provided by
uWSGI_. In a productive environment, we usually want to use a specialized webserver, such
as NGiNX_. This allows us to dispatch multiple server names on the same IPn address and to
terminate https-connections.


Run django-SHOP behind NGiNX
============================

In a production environment, usually you run these, and probably other containers behind a single
NGiNX instance. Additionally, since our customers normally do provide their user credentials and
other sensitive information, such as credit card numbers, we should ensure that our connection is
secured by https.

To do so, we run a separate composition of two Docker containers using this configuration:

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

Now we build and run the webserver.

.. code-block:: bash

	$ docker-compose -f nginx-compose.yml up --build -d

This spawns up two running Docker containers, where ``nginx-proxy`` is the actual webserver and
``letsencrypt-nginx-proxy-companion`` just manages the SSL certificates using the Let's Encrypt
certification authority. Note that you must point at least one DNS entry onto the IP address of
this host.


Run the django-SHOP container composition
=========================================

Each instance of a django-SHOP

Next edit ``docker-compose.yml``, locate the section ``wsgiapps`` and add 2 environment
variables and an additional network configuration:

.. code-block:: yaml
	:caption: docker-compose.yml

	  wsgiapp:
	    ...
	    environment:
	      ...
	      - VIRTUAL_HOST=djangoshop
	      - VIRTUAL_PROTO=uwsgi
	    ...
	    networks:
	      ...
	      - nginx-proxy
	    expose:
	      - 9009
	  ...
	  networks:
	    ...
	    - nginx-proxy:
	      external: true

Re-create and run the Docker containers using ``docker-compose up -d``.

Edit ``/etc/hosts`` and let ``djangoshop`` point onto 192.168.100.99 (the IP
address may vary depending on your Docker machine settings).

Point a browser onto http://djangoshop/ . It now is possible to browse the container through
NGiNX as proxy.


.. _uWSGI: http://uwsgi.readthedocs.org/
