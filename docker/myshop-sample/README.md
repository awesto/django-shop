# The merchant Docker image

This Dockerfile builds the final Docker image for **djangoSHOP**.
Copy these files into the merchants project and adopt the Dockerfile to their needs. Replace
``myshop-sample`` with whatever appropriate.

Build the image and create the container:

```
docker build -t myshop-sample .
docker create --name myshop-sample-initial -p 9001:9001 myshop-sample
```

Start the container:

```
docker start myshop-sample-initial
```

It may take some time until the container is ready, because beforehand the full-text search index
must be build.

Locate the IP address of your docker machine. Here we use 192.168.99.100, but depending your host's
operating system, run:

```
docker-machine env default
```

and locate that IP address using the environment variable DOCKER_HOST.

Point a browser onto http://192.168.99.100:9001/ or an alternative IP address. To access the
administration backend, change onto http://192.168.99.100:9001/admin and log in as "admin" using
password "secret".

To access the volume ``/web`` as provided by the container, start a throw away container:

```
docker run --rm -ti --volumes-from myshop-sample-initial myshop-sample /bin/bash
[root@97f8bf18bf5d example]# ll /web/logs
```

In ``/web/logs`` you may check for information provided by the services running in container
*myshop-sample-initial*. After saving or touching the file ``/web/workdir/myshop.ini``, the
Django application server restarts.

If done, stop and remove the container:

```
docker stop myshop-sample-initial
docker rm myshop-sample-initial
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
docker run --volumes-from myshop-sample-initial new-shop-image manage migrate
```

This presumes that the above image is executed as user *django* in the folder containing the
``manage.py`` command. Use ``USER`` and ``WORKDIR`` for this at the end of the merchant's
Dockerfile.
