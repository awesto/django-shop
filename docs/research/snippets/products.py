# This should be read as pseudo-code, it's not meant to be executable

# Just a rough draft/proposal of how the products could be handled, similar to what Satchmo does


class Product():
	# Product very general stuff goes here
	name = models.CharField(mx_length=255)
	


class ProductAttribute():
	'''
	'''
	name = 'ISBN number'
	type = 'String' # maybe not necessary?


class ProdcutAttributeValue():
	'''
	Not necesarly a real model: it's a M2M stub with a value attached, it may be better to implement
	in another way?
	'''
	attribute = models.ForeignKey(ProductAttribute)
	product = models.ForeignKey(Products)
	value = '0791040984' # Not a good idea to hard-code obviously, it's just an example


# This allows for interesting things, like category Attributes:

class CategoryAttribute():
	'''
	With a little managers magic, this allows to define a "Books" category, that
	adds an ISBN attribute to all the Products it contains.
	Another example: having a "Length" attribute for movies and music... etc.
	'''
	category = models.ForeignKey(Category) # Not defined here, it's easy to figure out
	attribute = models.ForeignKey(ProductAttribute)
	


	
