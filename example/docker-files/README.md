# The merchant Docker image

This Dockerfile builds the final Docker image for **django-SHOP**.
Copy the file ``Dockerfile`` and folder ``docker-images`` into the merchants project and adopt the
Dockerfile to their needs. Replace ``demo-shop`` with whatever appropriate.

Build the Docker image with:

```
cd django-shop
docker-compose up -d --build
```

Point a browser onto http://<docker-machine-ip>:9009/

In case you want to test one of the other examples, edit the file ``docker-compose.yml`` and locate
the subsection ``environment`` in section ``django``. Set ``DJANGO_SHOP_TUTORIAL`` to ``commodity``,
``i18n_commodity``, ``smartcard``, ``i18n_smartcard`` or ``polymorphic`` respectively.

It may take a few minutes until the container is ready, because beforehand the demo shop must be
initialized and the full-text search index must be build.

Locate the IP address of your docker machine. Here we use 192.168.99.100, but depending your host's
operating system, run:

```
docker-machine env default
```

and locate that IP address using the environment variable DOCKER_HOST.

Point a browser onto http://192.168.99.100:9001/ or your alternative IP address. To access the
administration backend, change onto http://192.168.99.100:9001/admin and log in as *admin* using
password *secret*.

The container keeps all non-reproducible data in a separate volume named ``shopmedia``, which can be
mounted by external containers.


## Running behind NGiNX

By default, uWSGI is configured to listen on port 9009 for HTTP requests. This allows us to attach
a browser directly onto the Docker machine's IP address. In a productive environment, we might want
to use NGiNX as a proxy in front of our Django application server. This allows us to proxy services
for multiple domains and to use https.

For this setup, please use the Docker image ``jwilder/nginx-proxy:latest`` and refer to it in a
separate ``docker-compose.yml`` file. Then add to the subsection ``environment`` of section
``django`` these environment variables:

```
  django:
    ...
    environment:
      - DJANGO_SHOP_TUTORIAL=i18n_polymorphic
      - VIRTUAL_HOST=myshop.example.com
      - VIRTUAL_PROTO=uwsgi
    ...
```

You should also remove the subsectiotion ``ports``, since we now do export this port externally.
Instead add the container to the network, in which the NGiNX proxy is running.
