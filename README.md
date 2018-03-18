# django-SHOP

[![Build Status](https://travis-ci.org/awesto/django-shop.svg?branch=master)](https://travis-ci.org/awesto/django-shop?branch=master)
[![PyPI version](https://img.shields.io/pypi/v/django-shop.svg)](https://pypi.python.org/pypi/django-shop)
[![Join the chat at https://gitter.im/awesto/django-shop](https://badges.gitter.im/awesto/django-shop.svg)](https://gitter.im/awesto/django-shop?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Software license](https://img.shields.io/pypi/l/django-shop.svg)](https://pypi.python.org/pypi/django-shop)
[![Twitter Follow](https://img.shields.io/twitter/follow/djangoSHOP.svg?style=social&label=djangoSHOP)](https://twitter.com/djangoSHOP)


## Run the demo projects using Docker

To get a first impression on **django-SHOP**, try out one of the six fully working demo projects.

```
git clone --depth=1 https://github.com/awesto/django-shop.git
cd django-shop
export DJANGO_SHOP_TUTORIAL=commodity
docker-compose up --build
```

Wait a few minutes until everything has been build and media files have been downloaded.
In the meantime find the IP address of your Docker machine using ``docker-machine ip``.

Point a browser onto http://<docker-machines-ip>:9009/

Change DJANGO_SHOP_TUTORIAL to ``i18n_commodity``, ``smartcard``, ``i18n_smartcard``,
``polymorphic`` or ``i18n_polymorphic`` and rebuild the container to run the other prepared
demos.

### Run the demo in a local virtualenv

Following the [introduction instructions](http://django-shop.readthedocs.io/en/latest/tutorial/intro.html)
should create a running shop in minutes, prefilled with a dozen of products. You can even pay by credit
card.


## Current Status of Django-SHOP

**Django-SHOP** aims to be a the easy, fun and fast e-commerce counterpart to **django-CMS**.

Specifically, we aim at providing a clean, modular and Pythonic/Djangonic implementation of an
e-commerce framework, that a moderately experienced Django developer should be able to pick up
and run easily.

Whenever possible, extra features shall be added to third party libraries. This implies that
**django-SHOP** aims to provide an API, which allows merchants to add every feature they desire.
