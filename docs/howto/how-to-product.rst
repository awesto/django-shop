========================
How to create a product
========================

Creating a product in django SHOP is really easy, but requires you to write 
python code.

Create a model
===============
The first step for you is to create a model to use as a product. We will create 
an example Book model together::

	from shop.models.productmodel import Product
	from django.db import models
	
	class Book(Product):
		isbn = models.CharField(max_length=255)
		
The following fields are already defined in the Product superclass:

* name : The name/title of the product
* slug : The slug used to refer to this product in the URLs
* short_description : a short description of the product
* long_description : A longer, more in-depth description of the product
* active : Products flagged as not active will not show in the lists
* date_added : The date at which the product was first created
* last_modified : A timestamp of when the product was last modified
* unit_price : The base price for one item
* category : An optional category for the product

Create a template
==================

Like other objects in Django, you will need to create a template to display
your model's contents to the world.
By default, your Product subclass will use the "shop/product_detail.html" 
template as a fallback, but will use your own template if you follow Django's
naming conventions: "appname/book_detail.html".

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
    
    # This is also possible - You retrieve a Product instance, with only the
    # fields defined in Product... but fear not! There is a way to get yours :)
    o = Product.objects.get(pk=...) # This gets a Product instance
    o = o.get_specific() # There, this is now an instance of MyProduct. Magic!
    
    # The opposite is of course possible as well:
    o = MyProduct.objects.get(pk=...) # a MyModel instance
    o = o.product # A Product instance
    o = o.get_specific() # Back to a MyModel instance
    
.. note:: This is possible thanks to using a Python __metaclass__, so the magic
          making it possible should be completely transparent to your Model.
          
Product variations
====================

By design, django SHOP does not include an out of the box solution to handling
product variations (colors, sizes...), in order to let implementors create their
own unrestricted. 

If you want such a pre-made solution for simple cases, we suggest you take a 
look at the `shop_simplevariations` "add-on" application, located at:

  https://github.com/chrisglass/django-shop-simplevariations