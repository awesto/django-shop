================
Getting started
================

Installation
=============

Here's the 1 minute guide to getting started with django SHOP and Django 1.2.x. 
Instructions for Django 1.3 will follow, but basically it means you don't need
django-cbv if you're using 1.3.

.. highlight:: bash

1. Create a normal Django project (we'll call it ``myshop`` for now)::

    django-admin startproject example
    cd example; django-admin startapp myshop

2. You'll want to use virtualenv::

    virtualenv . ; source bin/activate
    pip install django-cbv # only if using django<1.3
    pip install south
    pip install django-shop
    
.. highlight:: python

3. Go to your settings.py and configure your DB like the following, or anything
   matching your setup::

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


4. Add the following stuff to middlewares::

    MIDDLEWARE_CLASSES = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ] # <-- Notice how it's a square bracket (a list)? It makes life easier.
    
    import django # A quick and very dirty test to see if it's 1.3 yet...
    if django.VERSION[0] < 1 or django.VERSION[1] < 3:
        MIDDLEWARE_CLASSES.append('cbv.middleware.DeferredRenderingMiddleware')


5. Obviously, you need to add shop and myshop to your INSTALLED_APPS too::

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
    
6. Make the urls.py contain the following::

    from shop import urls as shop_urls # <-- Add this at the top
    
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

.. highlight:: bash

7. Most of the stuff you'll have to do is styling and templates work, so go ahead
   and create a templates directory in your project::
   
    cd example/myshop; mkdir -p templates/myshop
    
8. Lock and load::

    cd .. ; python manage.py syncdb --all ; python manage.py migrate --fake
    python manage.py runserver
    
9. Point your browser and marvel at the absence of styling::

    x-www-browser localhost:8000/shop

You now have a running but very empty django-shop installation.

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
        cover_picture = models.ImageField() 
        isbn = models.CharField(max_length=255)

        class Meta:
            ordering = ['author']
        

.. note:: The only limitation is that your product subclass must define a
   ``Meta`` class.

Like a normal Django model, you might want to register it to the admin interface
to allow easy edition by your users. In an ``admin.py`` file::

    from django.contrib import admin
    admin.site.register(Book)

That's it! 

Adding taxes
=============

Adding taxes calculation according to local regulations is also something that
you will be likely to have to do. It is relatively easy as well: create a new
file in your project, for example ``modifiers.py``, and add the following::

    import decimal    

    from shop.cart.cart_modifiers_base import BaseCartModifier
    
    class Fixed7PercentTaxRate(BaseCartModifier):
        """
        This will add 7% of the subtotal of the order to the total.

        It is of course not very useful in the real world, but this is an
        example.
        """
        
        def add_extra_cart_price_field(self, cart):
            taxes = decimal.Decimal('0.07') * cart.subtotal_price
            to_append = ('Taxes total', taxes)
            cart.extra_price_fields.append(to_append)
            return cart
            
You can now use this newly created tax modifier in your shop! To do so, simply
add the class to the list of cart modifiers defined in your ``settings.py`` file::

    SHOP_CART_MODIFIERS = ['myshop.modifiers.Fixed7PercentTaxRate']
    
Restart your server, and you should now see that a cart's total is dynamically
augmented to reflect this new rule.

You can implemented many other types of rules by overriding either this method
or other methods defined in
:class:`~shop.cart.cart_modifiers_base.BaseCartModifier`.

.. important:: Remember that cart modifiers are ordered! Like middlewares, the
               order in which they are declared in ``settings.SHOP_CART_MODIFIERS``
               matters.

