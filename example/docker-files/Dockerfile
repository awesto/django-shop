# cd django-shop
# docker build -f example/docker-files/Dockerfile .
FROM python:3.6
LABEL Description="Run django-SHOP demo" Maintainer="Jacob Rief <jacob.rief@gmail.com>"
RUN mkdir /web
WORKDIR /web
ARG DJANGO_WORKDIR=/web/workdir
ARG DJANGO_STATIC_ROOT=/web/staticfiles

# install packages outside of PyPI
RUN apt-get upgrade -y
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs optipng jpegoptim

# copy project relevant files into container
ADD setup.py /web/setup.py
ADD README.md /web/README.md
ADD shop /web/shop
ADD email_auth /web/email_auth
ADD example/myshop /web/myshop
ADD requirements /web/requirements
COPY example/wsgi.py /web/wsgi.py
COPY example/manage.py /web/manage.py
COPY example/package.json /web/package.json
COPY example/package-lock.json /web/package-lock.json
COPY example/docker-files/uwsgi.ini /web/uwsgi.ini
COPY example/requirements.txt /web/requirements/myshop.txt

# install project specific requirements
RUN pip install psycopg2-binary uWSGI 'Django<2.0' 'django-select2<6.1' 'django-angular<2.1'
RUN pip install .
RUN pip install -r /web/requirements/myshop.txt
RUN npm install
RUN useradd -M -d /web -s /bin/bash django

# handle static files
ENV DJANGO_STATIC_ROOT=$DJANGO_STATIC_ROOT
ENV DJANGO_WORKDIR=$DJANGO_WORKDIR
RUN mkdir -p $DJANGO_STATIC_ROOT/CACHE
RUN DJANGO_SHOP_TUTORIAL=commodity ./manage.py compilescss
RUN DJANGO_SHOP_TUTORIAL=commodity ./manage.py collectstatic --noinput --ignore='*.scss'
RUN chown -R django.django $DJANGO_STATIC_ROOT/CACHE

# handle media files in external volume
RUN mkdir -p $DJANGO_WORKDIR
RUN chown -R django.django $DJANGO_WORKDIR

# handle django-SHOP docs
#RUN git clone -b releases/0.13.x https://github.com/awesto/django-shop.git
#RUN cd django-shop/docs && make fragments

# expose service and volume to our internal Docker network
VOLUME $DJANGO_WORKDIR
