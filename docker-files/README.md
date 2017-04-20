# The django-SHOP Docker image

This Dockerfile builds an intermediate Docker image for **django-SHOP**. It shall be used as
base image to built the final merchant Docker image.

Build the image and create the container:

```
cd django-shop
docker build -t awesto/uwsgi-django-shop .
```

Since it's Dockerfile does not contain a ``CMD`` statement, starting that Docker image as a running
container, doesn't make much sense. However, one might want to look around and examine the file
structure.

To start the container, invoke:

```
docker run --rm -ti awesto/uwsgi-django-shop /bin/bash
[root@814575212aef example]# ls -l /usr/lib/python3.5/site-packages
```

By leaving the shell, using *CTRL-D* or typing ``exit``, this container is destroyed.


After the image has been build successfully, it should be tagged with the latest version
number.

```
docker tag awesto/uwsgi-django-shop awesto/uwsgi-django-shop:<latest-version-number>
```
