============
Architecture
============

This document should gather all the pre-code architecture requirements/research.

Core system
===========

Generally, the shop system can be seen as two different phases, with two different problems to solve:

The shopping phase:
-------------------

From a user perspective, this is where you shop around different product categories, and add desired products to
a shopping cart (or other abstraction). This is a very well-know type of website problematic from a user interface
perspective as well as from a model perspective: a simple "invoice" pattern for the cart is enough.

The complexity here is to start defining what a shop item should be.

The checkout process:
---------------------

As the name implies, this is a "workflow" type of problem: we must be able to add or remove steps to the checkout process depending
on the presence or absence of some plugins.
For instance, a credit-card payment plugin whould be able to insert a payment details page with credit card details in the general workflow.

To solve this we could implement a workflow engine. The person implementing the webshop whould then define the process using
the blocks we provide, and the system should then "run on its own".


Random ideas:
-------------

* class-based views
* class based plugins (not modules based!)


Plugin structure
================

Plugins should be class based, as most of the other stuff in Django is (for instace the admins), with the framework
defining both a base class for plugin writers to extend, as well as a registration method for subclasses.

Refer to snippets/plugins.py for a proposal by fivethreeo for a plugin structure.

Similar to the Django-CMS plugins, most of the shop plugins will probably have to render templates (for instance when
they want to define a new checkout step).
