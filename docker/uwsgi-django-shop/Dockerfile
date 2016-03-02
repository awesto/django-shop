FROM jrief/fedora-uwsgi-python:latest

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

ADD uwsgi.ini /etc/uwsgi.ini
RUN chown uwsgi.uwsgi /run/uwsgi

ADD elasticsearch.ini /etc/uwsgi.d/elasticsearch.ini
RUN chown elasticsearch.elasticsearch /etc/uwsgi.d/elasticsearch.ini

ADD redis.ini /etc/uwsgi.d/redis.ini
ADD redis.conf /etc/redis.conf
RUN chown redis.redis /etc/uwsgi.d/redis.ini

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install uwsgi

WORKDIR /usr/lib/python2.7
RUN pip install -e git+https://github.com/jrief/django-shop.git#egg=django-shop
WORKDIR /usr/lib/python2.7/src/django-shop
RUN npm install
RUN bower install --allow-root

RUN useradd -M -d /web -s /bin/bash django
RUN mkdir -p /web/{logs,workdir,elasticsearch,redis}
RUN chown -R django.django /web/{logs,workdir}
RUN chown -R elasticsearch.elasticsearch /web/elasticsearch
RUN chown -R redis.redis /web/redis
