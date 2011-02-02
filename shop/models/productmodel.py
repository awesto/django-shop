'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from django.db import models
from shop.util.fields import CurrencyField

class Category(models.Model):
    '''
    This should be a node in a tree (mptt?) structure representing categories 
    of products.
    Ideally, this should be usable as a tag cloud too (tags are just categories
    that are not in a tree structure). The display logic should be handle on a 
    per-site basis
    '''
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey('self', related_name="children",
                                        null=True, blank=True)
    
    def get_products(self):
        '''
        Gets the products belonging to this category (not recursively)
        '''
        return Product.objects.filter(category=self)
    
class ProductAttribute(models.Model):
    '''
    This is an example of how the attributes could work for products, if this 
    approach is chosen
    '''
    name = models.CharField(max_length=255)

class Product(models.Model):
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
    
    base_price = CurrencyField()
    
    category = models.ForeignKey(Category, null=True)
    
class ProductAttributeValue(models.Model):
    '''
    This is simply a M2M class with an extra field to the relation (the value of 
    an attribute for a give product)
    '''
    attribute = models.ForeignKey(ProductAttribute)
    product = models.ForeignKey(Product)
    value = models.TextField() # Does it make sense to use something smaller?