================
Getting started
================

Installation
=============
Here's the 5 minutes guide to getting started with django SHOP.


Virtualenv
----------
I strongly recommend to use virtualenv_, otherwise install it using the OS tool of choice:

.. _virtualenv: http://virtualenv.readthedocs.org/en/latest/

.. code-block:: bash

	sudo aptitude install virtualenv  # on Ubuntu or Debian
	sudo yum install virtualenv  # on Fedora, RedHat or CentOS
	sudo port install virtualenv  # on MacOS


Other Dependencies
------------------
Into the newly created virtual environment, install other Python software this project depends on:

.. code-block:: bash

	virtualenv . ; source bin/activate
	pip install south
	pip install django-shop
	pip install jsonfield

Optionally you may want to install an alternative Database connector such as ``mysqlclient`` or
``psycopg2``.

Since chances are high that you need a CMS in combination with this shop, let me mention that
Django-SHOP plays well together with Django-CMS.

Quite often


Create a Django App
-------------------
Create a normal Django project, we'll call it ``myshop`` for now:

.. code-block:: bash

	django-admin startproject myshop
	cd myshop
	mkdir -p myshop/{admin,models,views}
	touch myshop/{admin,models,views}/__init__.py


Materialize abstract models from Django-SHOP
--------------------------------------------
This is not a software out-of-the-box, but rather a framework helping you to create a customized
shop. Chances are very high, that you will override one ore more database models. Therefore all
models shipped with the shop are abstract and must be “materialized” by ``myshop``. Add these
stubs to your project:

``myshop/models/shopmodels.py``:

.. literalinclude:: samples/shopmodels.py


``myshop/admin/order.py``:

.. literalinclude:: samples/admin_order.py

and don't forget to import these Python modules in ``myshop/models/__init__.py`` and
``myshop/admin/__init__.py`` respectively.



Edit your application's ``settings.py``
---------------------------------------
Configure your DB connector:

.. code-block:: python

	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'NAME': 'test.sqlite',
	        'USER': '',
	        'PASSWORD': '',
	        'HOST': '',
	        'PORT': '',
	    }
	}


Add the following stuff to the middleware classes:

.. code-block:: python

	MIDDLEWARE_CLASSES = [
	    'django.middleware.common.CommonMiddleware',
	    'django.contrib.sessions.middleware.SessionMiddleware',
	    'django.middleware.csrf.CsrfViewMiddleware',
	    'django.contrib.auth.middleware.AuthenticationMiddleware',
	    'django.contrib.messages.middleware.MessageMiddleware',
	] # <-- Notice how it's a square bracket (a list)? It makes life easier.


Obviously, you need to add shop and myshop to your INSTALLED_APPS too:

.. code-block:: python

	INSTALLED_APPS = [
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    # Uncomment the next line to enable the admin:
	    'django.contrib.admin',
	    # Uncomment the next line to enable admin documentation:
	    'django.contrib.admindocs',
	    'polymorphic', # We need polymorphic installed for the shop
	    'south',
	    'shop', # The django SHOP application
	    'shop.addressmodel', # The default Address and country models
	    'myshop', # the project we just created
	]

Configure the URL routing

.. code-block:: python

	from shop import urls as shop_urls
	
	# Other stuff here
	
	urlpatterns = patterns('',
	    # Example:
	    #(r'^example/', include('example.foo.urls')),
	    # Uncomment the admin/doc line below to enable admin documentation:
	    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
	    # Uncomment the next line to enable the admin:
	    (r'^admin/', include(admin.site.urls)),
	    (r'^shop/', include(shop_urls)), # <-- That's the important bit
	    # You can obviously mount this somewhere else
	)

Create the database models and load them

.. code-block:: bash

	python manage.py schemamigration myshop
	python manage.py syncdb
	python manage.py migrate
	python manage.py runserver

Finally point your browser onto http://localhost:8000/shop and marvel at the absence of styling

You now have a running but very empty django SHOP installation.

Adding a custom product
========================
.. highlight:: python

Having a shop running is a good start, but you'll probably want to add at least
one product class that you can use to sell to clients!

The process is really simple: you simply need to create a class representing
your object in your project's ``models.py``. Let's start with a very simple model
describing a book::

    from shop.models import Product
    from django.db import models

    class Book(Product):
        # The author should probably be a foreign key in the real world, but
        # this is just an example
        author = models.CharField(max_length=255)
        cover_picture = models.ImageField(upload_to='img/book')
        isbn = models.CharField(max_length=255)

        class Meta:
            ordering = ['author']


.. note:: The only limitation is that your product subclass must define a
   ``Meta`` class.

Like a normal Django model, you might want to register it in the admin interface
to allow for easy editing by your admin users. In an ``admin.py`` file::

    from django.contrib import admin

    from models import Book

    admin.site.register(Book)

That's it!

Adding taxes
=============

Adding tax calculations according to local regulations is also something that
you will likely have to do. It is relatively easy as well: create a new
file in your project, for example ``modifiers.py``, and add the following::

    import decimal

    from shop.cart.cart_modifiers_base import BaseCartModifier

    class Fixed7PercentTaxRate(BaseCartModifier):
        """
        This will add 7% of the subtotal of the order to the total.

        It is of course not very useful in the real world, but this is an
        example.
        """

        def get_extra_cart_price_field(self, cart, request):
            taxes = decimal.Decimal('0.07') * cart.subtotal_price
            to_append = ('Taxes total', taxes)
            return to_append

You can now use this newly created tax modifier in your shop! To do so, simply
add the class to the list of cart modifiers defined in your ``settings.py`` file::

    SHOP_CART_MODIFIERS = ['myshop.modifiers.Fixed7PercentTaxRate']

Restart your server, and you should now see that a cart's total is dynamically
augmented to reflect this new rule.

You can implement many other types of rules by overriding either this method
or other methods defined in
:class:`~shop.cart.cart_modifiers_base.BaseCartModifier`.

.. important:: Remember that cart modifiers are ordered! Like middlewares, the
               order in which they are declared in ``settings.SHOP_CART_MODIFIERS``
               matters.

