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
* Indentation should be exactly 4 spaces. Not 2, not 6, not 8. **4**. Also, tabs
  are evil.
* We try (loosely) to keep the line length at 79 characters. Generally the rule
  is "it should look good in a terminal-base editor" (eg vim), but we try not be
  [Godwin's law] about it.
* Most pull requests will be rejected without proper unit testing
* Generally we like to discuss new features before they are merged in, but this
  is a somewhat flexible rule :)

Process
=======

This is how you fix a bug or add a feature:

#. `fork`_ us on GitHub.
#. Checkout your fork.
#. Hack hack hack, test test test, commit commit commit, test again.
#. Push to your fork.
#. Open a pull request.