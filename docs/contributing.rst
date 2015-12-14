=============
Contributing
=============

Naming conventions
==================

The official name of this project is **django SHOP**. Third party plugins for **django SHOP** shall
follow the same naming convention as for plugins of **djangoCMS**: Third party package names shall
start with **djangoshop** followed by a dash; no space shall be added between **django** and
**shop**.

**Django SHOP** should be capitalised at the start of sentences and in
title-case headings.

When referring to the package, repositories and any other things in which
spaces are not permitted, use **django-shop**.


Running tests
==============

It's important to run tests before committing :)


Setting up the environment
--------------------------

We highly suggest you run the tests suite in a clean environment, using a tool such as
`virtualenv <http://pypi.python.org/pypi/virtualenv>`_.

1. Clone the repository and cd into it::

    git clone https://github.com/jrief/django-shop
    cd django-shop

2. Create a virtualenv, and activate it::

    virtualenv ~/.virtualenvs/django-shop
    source ~/.virtualenvs/django-shop/bin/activate

3. Install the project in development mode::

    pip install -e .

4. Install the development requirements::

    pip install -r requirements/django18/testing.txt

That's it! Now, you should be able to run the tests::

    py.test tests

We use `tox <http://codespeak.net/tox/>`_ as a CI tool. To run the full CI
test suite and get a coverage report, all you have to do is this::

    pip install tox
    tox

If you work on a certain part of the code base and you want to run the related
tests and get a coverage report, you can do something like this::

    coverage run $(which py.test) tests/test_money.py \
        && coverage report -m shop/money/*.py

.. NOTE::
    Using tox and py.test is optional. If you prefer the conventional way of
    running tests, you can do this: ``django-admin.py test tests --settings shop.testsettings``

Community
==========

Most of the discussion around django SHOP takes place on IRC (Internet Relay
Chat), on the freenode servers in the #django-shop channel.

We also have a mailing list and a google group::

	http://groups.google.com/group/django-shop

Code guidelines
================

* Like most projects, we try to follow :pep:`8` as closely as possible
* Most pull requests will be rejected without proper unit testing
* Generally we like to discuss new features before they are merged in, but this
  is a somewhat flexible rule :)


Sending a pull request
======================

We use github for development, and so all code that you would like to see
included should follow the following simple workflow:

* Clone django-shop
* Checkout your fork
* Make a feature branch (to make pull requests easier)
* Hack hack, Test test, Commit commit, Test test
* Push your feature branch to your remote (your fork)
* Use the github interface to create a pull request from your branch
* Wait for the community to review your changes. You can hang out with us and
  ask for feedback on #django-shop (on freenode) in the mean time!
* If some changes are required, please commit to your local feature branch and
  push the changes to your remote feature branch. The pull request will be
  updated automagically with your new changes!
* DO NOT add unrelated commits to your branch, since they make the review
  process more complicated and painful for everybody.

More information can be found on Github itself:
http://help.github.com/send-pull-requests/
