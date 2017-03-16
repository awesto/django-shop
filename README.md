# django-SHOP

[![Build Status](https://travis-ci.org/awesto/django-shop.svg)](https://travis-ci.org/awesto/django-shop)
[![PyPI version](https://img.shields.io/pypi/v/django-shop.svg)](https://https://pypi.python.org/pypi/django-shop)
[![Join the chat at https://gitter.im/awesto/django-shop](https://badges.gitter.im/awesto/django-shop.svg)](https://gitter.im/awesto/django-shop?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Version 0.9 of **django-SHOP** is a complete rewrite of the old code base but keeps the concepts of
model overriding and cart modifiers. Therefore with some effort, it should be possible to migrate
existing projects to this new release. Please contact us, if you need help.


## NEWS

[![Twitter Follow](https://img.shields.io/twitter/follow/shields_io.svg?style=social&label=django-SHOP&maxAge=2592000)](https://twitter.com/djangoshop)

## Running the demo projects

To get a first impression on **django-SHOP**, try out the three full working demo projects.

And remember, I'm always happy to get some feedback on how it works elsewhere.


### Run the demo in a local virtualenv

Following the instructions  ``docs/tutorial/intro.rst`` and ``docs/tutorial/quickstart.rst``
should create a running shop in minutes, prefilled with a dozen of products.
You can even pay by credit card, if you apply for your own testing account at Stripe.


### Run the demo using Docker

A faster alternative to run the "polymorphic" demo of **django-SHOP** is to use a prepared Docker
container available on the [Docker Hub](https://hub.docker.com/r/awesto/demo-shop-polymorphic/).
If you have a running docker-machine, download and start the demo using:

```
docker run -p 9001:9001 --rm awesto/demo-shop-polymorphic:latest
```

Then point a browser on the IP address of your docker machine onto port 9001. If unsure invoke
``docker-machine ip``. This could for instance be http://192.168.99.100:9001/ .
To access the backend sign in with username *admin* and password *secret*. The first invocation
of each page takes some time, since beforehand the supplied images have to be thumbnailed.


## Current Status of Django-SHOP

This version of django-SHOP is currently used to implement real e-commerce sites. If you want
to help out, please have a look at our development documentation in ``docs/contributing.rst``.

**Django-SHOP** aims to be a the easy, fun and fast shop counterpart to django CMS.

Specifically, we aim at providing a clean, modular and Pythonic/Djangonic implementation of a shop
framework, that a moderately experienced Django programmer should be able to pick up and run easily.


### Please help

In order to build better demo sites, we need good pictures together with some introductory text
for arbitrary products. Both, pictures and text must be free of copyright or under an open license
(CC-by-SA, or similar). If you can provide these assets, please get in touch with Jacob Rief
or René Fleschenberg by email.

We also need ...
* more tests.
* translations into other natural languages.
* a native English speaker to check the documentation.
