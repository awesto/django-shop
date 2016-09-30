# uWSGI serving a django-shop application
# This Dockerfile builds the base image for all merchant implementations using **djangoSHOP**:
# docker build -t uwsgi-django-shop .

FROM awesto/fedora-uwsgi-python:latest

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

#RUN alternatives --install /usr/bin/python python /usr/bin/python3.4 2
#RUN alternatives --install /usr/bin/python python /usr/bin/python2.7 1
RUN pip install --upgrade pip

COPY docker-files/uwsgi.ini /etc/uwsgi.ini
RUN chown uwsgi.uwsgi /run/uwsgi

COPY docker-files/elasticsearch.ini /etc/uwsgi.d/elasticsearch.ini
RUN chown elasticsearch.elasticsearch /etc/uwsgi.d/elasticsearch.ini

COPY docker-files/redis.ini /etc/uwsgi.d/redis.ini
COPY docker-files/redis.conf /etc/redis.conf
RUN chown redis.redis /etc/uwsgi.d/redis.ini

RUN pip install uwsgi
ADD requirements /tmp/requirements
RUN pip install django==1.9.9
RUN pip install -r /tmp/requirements/py2.txt

RUN mkdir -p /web/{logs,workdir,elasticsearch,redis,django-shop}
COPY LICENSE.txt /web/django-shop
COPY README.md /web/django-shop
COPY MANIFEST.in /web/django-shop
COPY setup.py /web/django-shop
COPY package.json /web/django-shop
ADD email_auth /web/django-shop/email_auth
ADD shop /web/django-shop/shop
RUN pip install /web/django-shop

RUN useradd -M -d /web -s /bin/bash django
RUN chown -R django.django /web/{logs,workdir}
RUN chown -R elasticsearch.elasticsearch /web/elasticsearch
RUN chown -R redis.redis /web/redis
