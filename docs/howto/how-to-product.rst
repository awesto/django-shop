========================
How to create a product
========================

Creating a product in django SHOP is really easy, but requires you to write 
python code.

Create a model
===============
The first step for you is to create a model to use as a product. We will create 
an example Book model together::

	from shop.models import Product
	from django.db import models
	
	class Book(Product):
	    isbn = models.CharField(max_length=255)
            class Meta: pass

.. note:: Your product subclass must define a :class:`Meta` class. Usually, you will
   want to do so anyway, to define ordering and verbose names for example.
		
The following fields are already defined in the :class:`~shop.models.Product`
superclass:

.. class:: shop.models.Product

    .. attribute:: name

        The name/title of the product

    .. attribute:: slug

        The slug used to refer to this product in the URLs

    .. attribute:: active

        Products flagged as not active will not show in the lists

    .. attribute:: date_added

        The date at which the product was first created

    .. attribute:: last_modified

        A timestamp of when the product was last modified

    .. attribute:: unit_price

        The base price for one item


Create a template
==================

Like other objects in Django, you will need to create a template to display
your model's contents to the world.

By default, your :class:`~shop.models.Product` subclass will use
the ``shop/product_detail.html`` template as a fallback, but will use your own
template if you follow Django's naming conventions: ``appname/book_detail.html``.

That's all there is to it :)


Using your newly created Product
=================================

Your product should behave like a normal Django model in all circumstances. You 
should register it to admin (and create an admin class for it) like a normal 
model.

Code wise, the following options are possible to retrieve your newly
created model::

    # This gets your model's instance the normal way, you get both your model's
    # fields and the Product fields
    o = MyProduct.objects.get(pk=...)
    
    # This is also possible - You retrieve a MyProduct instance, using the 
    # Product manager
    o = Product.objects.get(pk=...)
    
.. note:: This is possible thanks to the terrific django_polymorphic dependency
          
Product variations
====================

By design, django SHOP does not include an out of the box solution to handling
product variations (colors, sizes...), in order to let implementors create their
own unrestricted. 

If you want such a pre-made solution for simple cases, we suggest you take a 
look at the `shop_simplevariations`_ "add-on" application.

.. _shop_simplevariations: https://github.com/chrisglass/django-shop-simplevariations
