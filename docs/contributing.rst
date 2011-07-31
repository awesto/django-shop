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

* As most projects, we try to follow PEP8_ as closely as possible
* Most pull requests will be rejected without proper unit testing
* Generally we like to discuss new features before they are merged in, but this
  is a somewhat flexible rule :)
  
.. _PEP8: http://www.python.org/dev/peps/pep-0008/