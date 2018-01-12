# cd django-shop
# docker build -f example/docker-files/Dockerfile .
FROM python:3.6
LABEL Description="Run django-SHOP demo" Maintainer="Jacob Rief <jacob.rief@gmail.com>"
RUN mkdir /web
WORKDIR /web

# copy project relevant files into container
ADD shop /web/shop
ADD email_auth /web/email_auth
ADD example/myshop /web/myshop
ADD requirements /web/requirements
COPY example/wsgi.py /web/wsgi.py
COPY example/manage.py /web/manage.py
COPY example/package.json /web/package.json
COPY example/package-lock.json /web/package-lock.json
COPY example/docker-files/uwsgi.ini /web/uwsgi.ini
COPY example/requirements.txt /web/requirements/example.txt

# install project specific requirements
RUN pip install 'Django<2.0' uWSGI
RUN pip install -r /web/requirements/example.txt

# install packages outside of PyPI
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN npm install

# handle static files
RUN mkdir /web/workdir
RUN mkdir /web/workdir/media
RUN mkdir /web/workdir/static
ENV DJANGO_WORKDIR=/web/workdir
ARG DJANGO_SHOP_TUTORIAL=commodity
ENV DJANGO_SHOP_TUTORIAL ${DJANGO_SHOP_TUTORIAL}
RUN ./manage.py compilescss
RUN ./manage.py collectstatic --noinput --ignore='*.scss'
RUN useradd -M -d /web -s /bin/bash django
RUN chown -R django.django /web/workdir

# handle django-SHOP docs
#RUN git clone -b releases/0.13.x https://github.com/awesto/django-shop.git
#RUN cd django-shop/docs && make fragments

# expose service and volume to our internal Docker network
VOLUME /web/workdir/media
EXPOSE 9009
CMD ["uwsgi", "--ini", "uwsgi.ini"]
