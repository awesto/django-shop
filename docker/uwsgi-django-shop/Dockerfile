FROM jrief/fedora-uwsgi-python:latest

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

#RUN alternatives --install /usr/bin/python python /usr/bin/python3.4 2
#RUN alternatives --install /usr/bin/python python /usr/bin/python2.7 1
RUN pip install --upgrade pip

ADD uwsgi.ini /etc/uwsgi.ini
RUN chown uwsgi.uwsgi /run/uwsgi

ADD elasticsearch.ini /etc/uwsgi.d/elasticsearch.ini
RUN chown elasticsearch.elasticsearch /etc/uwsgi.d/elasticsearch.ini

ADD redis.ini /etc/uwsgi.d/redis.ini
ADD redis.conf /etc/redis.conf
RUN chown redis.redis /etc/uwsgi.d/redis.ini

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install uwsgi https://github.com/awesto/django-shop/archive/master.zip

RUN useradd -M -d /web -s /bin/bash django
RUN mkdir -p /web/{logs,workdir,elasticsearch,redis}
RUN chown -R django.django /web/{logs,workdir}
RUN chown -R elasticsearch.elasticsearch /web/elasticsearch
RUN chown -R redis.redis /web/redis
