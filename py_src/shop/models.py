'''
Models.py for django-shop

This is a work in progress!

'''
from django.db.models.base import ModelBase
from django.db import models

class Product(ModelBase):
    '''
    A basic product for the shop
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property
    '''
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    long_description = models.TextField()
    active = models.BooleanField(default = False)

class Cart(ModelBase):
    '''
    This should be a rather simple list of items. Ideally it should be bound to
    a session and not to a User is we want to let people buy from our shop 
    without having to register with us.
    '''
    
class Cartitem(ModelBase):
    '''
    This is a holder for the quantity of items in the cart and, obviously, a 
    pointer to the actual Product being purchased :)
    '''
    quatity = models.IntegerField()
    product = models.ForeignKey(Product)

class Category(ModelBase):
    '''
    This should be a node in a tree (mptt?) structure representing categories 
    of products.
    Ideally, this should be usable as a tag cloud too (tags are just categories
    that are not in a tree structure). The display logic should be handle on a 
    per-site basis
    '''
    
class ProductAttribute(ModelBase):
    '''
    This is an example of how the attributes could work for products, if this 
    approach is chosen
    '''
    name = models.CharField(max_length=255)

class ProductAttributeValue(ModelBase):
    '''
    This is simply a M2M class with an extra field to the relation (the value of 
    an attribute for a give product)
    '''
    attribute = models.ForeignKey(ProductAttribute)
    product = models.ForeignKey(Product)
    value = models.TextField() # Does it make sense to use something smaller?

