# The merchant Docker image

This Dockerfile builds the final Docker image for **django-SHOP**.
Copy the file ``Dockerfile`` and folder ``docker-images`` into the merchants project and adopt the
Dockerfile to their needs. Replace ``demo-shop`` with whatever appropriate.

Build the Docker image with:

```
cd django-shop/example
docker build -t awesto/django-shop-demo .
```

Create and start the Docker container with:

```
docker create --name demo-shop-i18n_polymorphic --env DJANGO_SHOP_TUTORIAL=i18n_polymorphic -p 9001:9001 awesto/django-shop-demo
docker start demo-shop-i18n_polymorphic
```

In case you want to test one of the other examples, set the environment variable
``DJANGO_SHOP_TUTORIAL`` to ``commodity``, ``i18n_commodity``, ``smartcard``, ``i18n_smartcard`` or
``polymorphic`` respectively. To prevent confusion, also use another name for the container.

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

The container keeps all non-reproducible data in a separate volume named ``/web``, which can be
mounted by external containers. To access this volume, start a throw away container with:

```
docker run --rm -ti --volumes-from demo-shop-i18n_polymorphic django-shop-demo /bin/bash
[root@97f8bf18bf5d example]# ll /web/logs
```

In ``/web/logs`` you may check for information provided by the services running in container
``demo-shop-i18n_polymorphic``. The logfile ``uwsgi.log`` contains startup logs from uWSGI, while
``shop.log`` contains the logs from the Django application.

After saving or touching the file ``/web/workdir/myshop.ini``, the Django application server
restarts.

If done, stop and remove the container:

```
docker stop demo-shop-i18n_polymorphic
docker rm demo-shop-i18n_polymorphic
```

## Separation of code from data

Docker makes it very easy to separate code from data by providing sharable volumes. Therefore
whenever we have to rebuild a new version of the merchant's project, we create a separate Dockerfile
used to build a new Docker image. This image then shall be built inside the merchant's docker
folder.

**Do not add ``VOLUME /web`` to this Docker file**

```
docker build -t new-shop-image .
```

If database migrations are required, run them from the host's command line:

```
docker run --volumes-from demo-shop-i18n_polymorphic new-shop-image manage migrate
```

This presumes that the above image is executed as user *django* in the folder containing the
``manage.py`` command. Use ``USER`` and ``WORKDIR`` for this at the end of the merchant's
Dockerfile.
