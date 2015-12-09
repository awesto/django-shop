# Breaking News

Today, as of 2015-12-05, I finally finished three demos which should run out of the box.

Please read the files ``docs/tutorial/intro.rst`` and ``docs/tutorial/quickstart.rst``. Following
the instructions should create a running shop in minutes, prefilled with a dozen of products.
You can even pay by credit card, if you apply for your own testing account at Stripe.

I would be happy to get some feedback.


# django SHOP

This version of django-shop is currently under active development. If you want
to help out, please have a look at our `Development documentation in the
``DEVELOPMENT.rst`` file.

This repository hosts the django SHOP code and documentation.

Django SHOP aims to be the easy, fun and fast shop counterpart to django CMS.

Specifically, we aim at providing a clean, modular and Pythonic/Djangonic implementation of a shop
framework, that a moderately talented Django programmer should be able to pick up and run easily.

The current state is a roughly functional and highly modular system. Please refer to
docs/plugins.rst to figure out what plugin types are available, and what the do.

You'll find the detailed doc on `RTD <http://readthedocs.org/projects/django-shop/>`_


## Build status

.. |travisci| image:: https://api.travis-ci.org/divio/django-shop.png
.. _travisci https://travis-ci.org/divio/django-shop

|travisci|


## How to help:

* Development is done on github - please fork!
* Most of the discussion around architecture decisions / tools etc... take
  place on IRC (Freenode), on #django-shop
* Pick a task from the list below :)


## Todo:

* Somebody should kickstart an example shop application using django SHOP, to
  use as an example.
* If you feel like adding templates, please *refrain* from adding fancy styling
  to the core set of templates.
  Styling is awesome, and everybody wants a good looking shop, but it should go
  in example apps, not in core shop :)
  Also, please keep templates to the main templates directory only (so that
  people have a clear view of the templates structure)
* Writing docs is most welcome :)
* Refactoring tests to make creating test environments less messy (fixtures?)
* If you feel like you could solve having multiple currencies in an elegant
  manner, we would really be interested to hear from you
