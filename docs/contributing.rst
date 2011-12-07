=============
Contributing
=============

Running tests
==============

It's important to run tests before committing :)

Thankfully, we provided a small yet handy script to do it for you! Simply
invoke ``runtests.sh`` on a unix platform and you should be all set.

Options
--------

While a simple tool, ``runtests.sh`` provides the following options:

* ``--with-coverage`` : run the tests using coverage and let the coverage results
  be displayed in your default browser
* ``--with-docs`` : run the tests and generate the documentation (the one you're
  reading right now).

Community
==========

Most of the discussion around django SHOP takes place on IRC (Internet Relay
Chat), on the freenode servers in the #django-shop channel

We also have a mailing list and a google group::

	http://groups.google.com/group/django-shop

Code guidelines
================

* As most projects, we try to follow :pep:`8` as closely as possible
* Most pull requests will be rejected without proper unit testing
* Generally we like to discuss new features before they are merged in, but this
  is a somewhat flexible rule :)


Sending a pull request
======================

We use github for development, and so all code that you would like to see
included into should follow the following simple workflow:

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
