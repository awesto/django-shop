.. _tutorial/polymorphic-product:

==================================
Products with Different Properties
==================================

In the previous examples we have seen that we can model our products according to their physical
properties, but what if we want to sell another type of a product with different properties. This
is where polymorphism_ enters the scene.

.. _polymorphism: https://en.wikipedia.org/wiki/Polymorphism_(computer_science)


Run the Polymorphic Demo
========================

To test this example, set the shell environment variable ``export DJANGO_SHOP_TUTORIAL=polymorphic``,
then recreate the database as explained in :ref:`tutorial/create-demo-database` and start the demo
server:

.. code-block:: shell

	./manage.py runserver


The Polymorphic Product Model
=============================

If in addition to Smart Cards we also want to sell Smart Phones, we must declare a new model.
Here instead of duplicating all the common fields, we unify them into a common base class named
``Product``. Then that base class shall be extended to become either our known model ``SmartCard``
or a new model ``SmartPhone``.

To enable polymorphic models in **djangoSHOP**, we require the application django-polymorphic_.
Here our models for Smart Cards or Smart Phones will be split up into a generic part and a
specialized part. The generic part goes into our new ``Product`` model, whereas the specialized
parts remain in their models.

You should already start to think about the layout of the list views. Only attributes in model
``Product`` will be available for list views displaying Smart Phones side by side with Smart Cards.
First we must create a special `Model Manager`_ which unifies the query methods for translatable
and polymorphic models:

.. _django-polymorphic: https://django-polymorphic.readthedocs.org/en/latest/
.. _Model Manager: https://docs.djangoproject.com/en/stable/topics/db/managers/

.. literalinclude:: /../example/myshop/models/polymorphic/product.py
	:caption: myshop/models/i18n/polymorphic/product.py
	:linenos:
	:language: python
	:lines: 8-15, 17-19, 21-23, 26-30, 43

The next step is to identify which model attributes qualify for being part of our Product
model. Unfortunately, there is no silver bullet for this problem and that's one of the reason why
**djangoSHOP** is shipped without any prepared model for it. If we want to sell both Smart Cards
and Smart Phones, then this Product model may do its jobs:

.. literalinclude:: /../example/myshop/models/polymorphic/product.py
	:caption: myshop/models/i18n/polymorphic/product.py
	:linenos:
	:language: python
	:lines: 31-39


Model for Smart Card
--------------------

The model used to store translated fields is the same as in our last example. The new model for
Smart Cards now inherits from Product:

.. literalinclude:: /../example/myshop/models/polymorphic/smartcard.py
	:caption: myshop/models/i18n/polymorphic/smartcard.py
	:linenos:
	:language: python
	:lines: 4-8, 10-24


Model for Smart Phone
---------------------

The product model for Smart Phones is intentionally a little bit more complicated. Not only does
it have a few more attributes, but Smart Phones can be sold with different specifications of
internal storage. The latter influences the price and the product code. This is also the reason why
we didn't move the model fields ``unit_price`` and ``products_code`` into our base class
``Product``, although every product in our shop requires them.

When presenting Smart Phones in our list views, we want to focus on different models, but not on
each flavor, ie. its internal storage. Therefore customers will have to differentiate between
the concrete Smart Phone variations, whenever they add them to their cart, but not when viewing them
in the catalog list. For a customer, it would be very boring to scroll through lists with many
similar products, which only differentiate by a few variations.

This means that for some Smart Phone models, there is be more than one *Add to cart* button.

When modeling, we therefore require two different classes, one for the Smart Phone model and one
for each Smart Phone variation.

.. literalinclude:: /../example/myshop/models/polymorphic/smartphone.py
	:caption: myshop/models/polymorphic/smartphone.py
	:linenos:
	:language: python
	:lines: 7-10, 20-44

Here the method ``get_price()`` can only return the minimum, average or maximum price for our
product. In this situation, most merchants extol the prices as: *Price starting at € 99.50*.

The concrete Smart Phone then is modeled as:

.. literalinclude:: /../example/myshop/models/polymorphic/smartphone.py
	:linenos:
	:language: python
	:lines: 94-103


To proceed with purchasing, customers need some :ref:`tutorial/cart-checkout` pages.


Model for a generic Commodity
-----------------------------

For demo purposes, this polymorphic example adds another kind of Product model, a generic Commodity.
Here instead of adding every possible attribute of our product to the model, we try to remain as
generic as possible, and instead use a ``PlaceholderField`` as provided by **djangoCMS**.

.. code-block:: python
	:caption:myshop/models/commodity.py

	from cms.models.fields import PlaceholderField
	from myshop.models.product import Product
	
	class Commodity(Product):
	    # other product fields
	    placeholder = PlaceholderField("Commodity Details")

This allows us to add any arbitrary information to our product's detail page. The only requirement
for this to work is, that the rendering template adds a templatetag to render this placeholder.

Since the **djangoSHOP** framework looks in the folder ``catalog`` for a template named after its
product class, adding this HTML snippet should do the job:

.. code-block:: django
	:caption:myshop/catalog/commodity-detail.html

	{% extends "myshop/pages/default.html" %}
	{% load cms_tags %}
	
	<div class="container">
		<div class="row">
			<div class="col-xs-12">
				<h1>{% render_model product "product_name" %}</h1>
				{% render_placeholder product.placeholder %}
			</div>
		</div>
	</div>

This detail template extends the default template of our site. Apart from the product's name (which
has added as a convenience), this view remains empty when first viewed. In *Edit* mode, double
clicking on the heading containing the product name, opens the detail editor for our commodity.

After switching into *Structure* mode, a placeholder named ``Commodity Details`` appears. Here we
can add as many Cascade plugins as we want, by subdividing our placeholder into rows, columns,
images, text blocks, etc. It allows us to edit the detail view of our commodity in whatever layout
we like. The drawback using this approach is, that it can lead to inconsistent design and is much
more labor intensive, than just editing the product's attributes together with their appropriate
templates.


Configure the Placeholder
~~~~~~~~~~~~~~~~~~~~~~~~~

Since we use this placeholder inside a hard-coded Bootstrap column, we must provide a hint to
Cascade about the widths of that column. This has to be done in the settings of the project:

.. code-block:: python
	:caption:myshop/settings.py

	CMS_PLACEHOLDER_CONF = {
	  ...
	  'Commodity Details': {
	    'plugins': ['BootstrapRowPlugin', 'TextPlugin', 'ImagePlugin', 'PicturePlugin'],
	    'text_only_plugins': ['TextLinkPlugin'],
	    'parent_classes': {'BootstrapRowPlugin': []},
	    'require_parent': False,
	    'glossary': {
	      'breakpoints': ['xs', 'sm', 'md', 'lg'],
	      'container_max_widths': {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170},
	      'fluid': False,
	      'media_queries': {
	        'xs': ['(max-width: 768px)'],
	        'sm': ['(min-width: 768px)', '(max-width: 992px)'],
	        'md': ['(min-width: 992px)', '(max-width: 1200px)'],
	        'lg': ['(min-width: 1200px)'],
	      },
	    }
	  },
	  ...
	}

This placeholder configuration emulates the Bootstrap column as declared by
``<div class="col-xs-12">``. 
