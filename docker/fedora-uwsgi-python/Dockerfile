FROM fedora:22

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

RUN dnf upgrade -y
RUN dnf install -y wget git gcc gcc-c++ tar python-devel python3-devel procps-ng
RUN dnf install -y uwsgi uwsgi-plugin-python uwsgi-plugin-python3
RUN dnf install -y python-uwsgidecorators python3-uwsgidecorators 
RUN dnf install -y uwsgi-plugin-gevent uwsgi-plugin-greenlet uwsgi-logger-file
RUN dnf install -y libjpeg-turbo-devel libpng-devel freetype-devel optipng jpegoptim mailcap
RUN dnf install -y redis java npm

RUN rpm -i https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.4.noarch.rpm
RUN npm install -g bower
