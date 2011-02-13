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

