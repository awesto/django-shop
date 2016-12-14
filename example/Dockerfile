FROM awesto/uwsgi-django-shop:latest

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

# install packages outside of PyPI
WORKDIR /web/django-shop
RUN npm install

# copy the example project
RUN mkdir -p /web/django-shop/example
ADD myshop /web/django-shop/example/myshop
COPY docker-files/wsgi.py /web/django-shop/example/wsgi.py
COPY manage.py /web/django-shop/example/manage.py

# add uwsgi.ini file into workdir, so that touching this file restarts the Django server
COPY docker-files/myshop.ini /web/workdir/myshop.ini
RUN ln -s /web/workdir/myshop.ini /etc/uwsgi.d/myshop.ini

# convert SASS into css files
ENV DJANGO_SHOP_TUTORIAL=polymorphic DJANGO_WORKDIR=/web/workdir
RUN example/manage.py compilescss
RUN example/manage.py collectstatic --noinput --ignore='*.scss'

# add file removed after bootstrapping uwsgi
RUN touch /web/workdir/.bootstrap
RUN chown -R django.django /web/workdir

VOLUME /web

# when enabling the CMD disable deamonize in uwsgi.ini
EXPOSE 9001
CMD ["/usr/sbin/uwsgi", "--ini", "/etc/uwsgi.ini"]
