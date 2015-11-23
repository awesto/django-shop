==================================
Products with different properties
==================================

In the previous examples we have seen that we can model our products according to their physical
properties, but what if we want to sell another type of product with different properties. This
is where polymorphism_ enters the scene.

.. _polymorphism: https://en.wikipedia.org/wiki/Polymorphism_(computer_science)


Run the Polymorphic demo
========================

To test this example, set the shell environment variable ``export DJANGO_SHOP_TUTORIAL=polymorphic``,
then recreate the database as explained in :ref:`create-demo-database`.

Afterwards start the demo server:

.. code-block:: shell

	./manage.py runserver


The Polymorphic Product Model
=============================

If in addition to Smart Cards we want to sell Smart Phones, we must declare a new model. Here
instead of duplicating all the common fields, we unify them into a common base class named
``Product``. Then that base class shall be extended to become either our model ``SmartCard`` or
a model ``SmartPhone``.

To enable polymorphic models in **djangoSHOP**, we require the application django-polymorphic_.
Here our models for Smart Cards or Smart Phones will be split up into a generic part and a
specialized part. The generic part goes into our new ``Product`` model. Here you should already
think about the layout of the list views. Only attributes in the ``Product`` will be available for
list views displaying Smart Phones side by side with Smart Cards. First we must create a special
`Model Manager`_ which unifies the query methods for translatable and polymorphic models:

.. _django-polymorphic: https://django-polymorphic.readthedocs.org/en/latest/
.. _Model Manager: https://docs.djangoproject.com/en/stable/topics/db/managers/

.. literalinclude:: /../example/myshop/models/polymorphic/product.py
	:caption: myshop/models/i18n/polymorphic/product.py
	:linenos:
	:language: python
	:lines: 9-10, 13, 16-27

The next step is to identify which model attributes qualify for being part of our Product
model. Unfortunately there is no silver bullet for this problem and that's the reason why
**djangoSHOP** is shipped without any prepared model for this. If we want to sell both Smart Cards
and Smart Phones, then this Product model will do its jobs:

.. literalinclude:: /../example/myshop/models/polymorphic/product.py
	:linenos:
	:language: python
	:lines: 7, 13-14, 28-46

The model used to store translated fields is the same as in our last example. The new model for
Smart Cards now becomes a subset of itself:

.. literalinclude:: /../example/myshop/models/polymorphic/smartcard.py
	:caption: myshop/models/i18n/polymorphic/smartcard.py
	:linenos:
	:language: python
	:lines: 7-9, 12-21

The product model for Smart Phones (intentionally) is a little bit more complicated. Not only does
it have a few more attributes, but Smart Phones can be sold with different specifications of
internal storage. The latter influences the price and the product code. This also is the reason why
our base Product model does not contain the fields ``unit_price`` and ``products_code``, although
every product in our shop requires them.

When presenting Smart Phones in our list views, we want to focus on different models, but not on
each markedness, ie. its internal storage. Therefore customers can differentiate between the
concrete Smart Phone variations, whenever they add them to their cart. This means, that for some
Smart Phone models, there might be more than one *Add to cart* button.

When modeling, we therefore require two different classes, one for the Smart Phone model and one
for each Smart Phone variation.

.. literalinclude:: /../example/myshop/models/polymorphic/smartphone.py
	:caption: myshop/models/polymorphic/smartphone.py
	:linenos:
	:language: python
	:lines: 10-11, 14, 28-47

Here the method ``get_price()`` can only return the minimum, average or maximum price for our
product, but that's something often seen quite often in stores, where stated: *Price starting
at € 99.50*.

The concrete Smart Phone then is modeled as:

.. literalinclude:: /../example/myshop/models/polymorphic/smartphone.py
	:linenos:
	:language: python
	:lines: 90-99
