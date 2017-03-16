# uWSGI serving a django-shop application
# This Dockerfile builds the base image for all merchant implementations using **django-SHOP**:
# docker build -t awesto/uwsgi-django-shop .

FROM awesto/fedora-uwsgi-python:latest

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

RUN alternatives --install /usr/bin/python python /usr/bin/python3.5 2
RUN alternatives --install /usr/bin/python python /usr/bin/python2.7 1
RUN pip install --upgrade pip

COPY docker-files/uwsgi.ini /etc/uwsgi.ini
RUN chown uwsgi.uwsgi /run/uwsgi

COPY docker-files/elasticsearch.ini /etc/uwsgi.d/elasticsearch.ini
RUN chown elasticsearch.elasticsearch /etc/uwsgi.d/elasticsearch.ini

COPY docker-files/redis.ini /etc/uwsgi.d/redis.ini
COPY docker-files/redis.conf /etc/redis.conf
RUN chown redis.redis /etc/uwsgi.d/redis.ini

RUN cat /etc/resolv.conf
RUN pip install uwsgi
ADD requirements /tmp/requirements
RUN pip install Django==1.10.5
RUN pip install -r /tmp/requirements/common.txt

# copy the local django-shop file into a temporary folder
RUN mkdir -p /tmp/django-shop
COPY LICENSE.txt /tmp/django-shop
COPY README.md /tmp/django-shop
COPY MANIFEST.in /tmp/django-shop
COPY setup.py /tmp/django-shop
ADD email_auth /tmp/django-shop/email_auth
ADD shop /tmp/django-shop/shop
# and from there install it into the site-package using setup.py
RUN pip install /tmp/django-shop
RUN rm -rf /tmp/django-shop

RUN mkdir -p /web/{logs,workdir,elasticsearch,redis}
RUN mkdir -p /web/logs/elasticsearch
RUN useradd -M -d /web -s /bin/bash django
RUN chown -R django.django /web/{logs,workdir}
RUN chown -R elasticsearch.elasticsearch /web/elasticsearch /web/logs/elasticsearch
RUN chown -R redis.redis /web/redis
