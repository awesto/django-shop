FROM awesto/uwsgi-django-shop:latest

LABEL Description="Run one of 6 django-SHOP demos" Maintainer="Jacob Rief <jacob.rief@gmail.com>"

# copy the example project
RUN mkdir -p /web/demo-shop
ADD myshop /web/demo-shop/myshop
COPY docker-files/wsgi.py /web/demo-shop/wsgi.py
COPY manage.py /web/demo-shop/manage.py
COPY package.json /web/demo-shop/package.json

# install packages outside of PyPI
WORKDIR /web/demo-shop
RUN npm install

# add uwsgi.ini file into workdir, so that touching this file restarts the Django server
COPY docker-files/myshop.ini /web/workdir/myshop.ini
RUN ln -s /web/workdir/myshop.ini /etc/uwsgi.d/myshop.ini

# convert SASS into css files
ENV DJANGO_WORKDIR=/web/workdir
RUN DJANGO_SHOP_TUTORIAL=commodity ./manage.py compilescss
RUN DJANGO_SHOP_TUTORIAL=commodity ./manage.py collectstatic --noinput --ignore='*.scss'
RUN chown -R django.django /web/workdir

VOLUME /web

# when enabling the CMD disable deamonize in uwsgi.ini
EXPOSE 9001
CMD ["/usr/sbin/uwsgi", "--ini", "/etc/uwsgi.ini"]
