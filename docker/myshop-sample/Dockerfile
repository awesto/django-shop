FROM uwsgi-django-shop:latest

MAINTAINER Jacob Rief <jacob.rief@gmail.com>

# checkout the merchant's project
# Here this is not required for myshop-sample, because the example is already
# shipped with django-shop, but normally each merchant has is own repository.

# add uwsgi ini file into workdir, so that touching this file restarts the Django server
ADD myshop.ini /web/workdir/myshop.ini
RUN ln -s /web/workdir/myshop.ini /etc/uwsgi.d/myshop.ini

# add media files
WORKDIR /web
RUN wget -q -O- http://downloads.django-shop.org/django-shop-workdir.tar.gz | tar zx

# create database and populate static files
WORKDIR /usr/lib/python2.7/src/django-shop/example
ENV DJANGO_SHOP_TUTORIAL=polymorphic DJANGO_WORKDIR=/web/workdir DJANGO_SETTINGS_MODULE=myshop.settings
RUN ./manage.py migrate
RUN ./manage.py loaddata fixtures/myshop-$DJANGO_SHOP_TUTORIAL.json
RUN ./manage.py compilescss
RUN ./manage.py collectstatic --noinput --ignore='*.scss'
RUN touch /web/workdir/bootstrap
RUN chown -R django.django /web/workdir

VOLUME /web

# when enabling the CMD disable deamonize in uwsgi.ini
EXPOSE 9001
CMD ["/usr/sbin/uwsgi", "--ini", "/etc/uwsgi.ini"]
