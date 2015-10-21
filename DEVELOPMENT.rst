===========
Development
===========

Quickstart
==========
Want to help out? Great! Here are some instructions to get you up and running.

We recommend that you use virtualenv_.

1. Clone the repository and cd into it::

    git clone https://github.com/jrief/django-shop
    cd django-shop

2. Create a virtualenv, and activate it::

    virtualenv ~/.virtualenvs/django-shop
    source ~/.virtualenvs/django-shop/bin/activate

3. Install the project in development mode::

    pip install -e .

4. Install the development requirements::

    pip install -r requirements/dev.txt

That's it! Now, you should be able to run the tests::

    py.test tests

We use tox_ as a CI tool. To run the full CI test suite and get a coverage
report, all you have to do is this::

    tox

If you work on a certain part of the code base and you want to run the related
tests and get a coverage report, you can do something like this::

    coverage run $(which py.test) tests/test_money.py && coverage report -m shop/money/*.py

.. NOTE::
    Using tox and py.test is optional. If you prefer the conventional way of
    running tests, you can do this: ``django-admin.py test tests --settings shop.testsettings``

.. _virtualenv: https://virtualenv.pypa.io/
.. _tox: http://codespeak.net/tox/
