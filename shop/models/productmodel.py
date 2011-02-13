# -*- coding: utf-8 -*-
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
    slug = models.SlugField()
    parent_category = models.ForeignKey('self', related_name="children",
                                        null=True, blank=True)
    
    def get_products(self):
        '''
        Gets the products belonging to this category (not recursively)
        '''
        return Product.objects.filter(category=self)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"
        app_label = 'shop'

class ProductManager(models.Manager):
    
    def active(self):
        return self.filter(active=True)

class Product(models.Model):
    '''
    A basic product for the shop
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property
    '''
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    short_description = models.CharField(max_length=255)
    long_description = models.TextField()
    active = models.BooleanField(default=False)
    
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    unit_price = CurrencyField()
    
    category = models.ForeignKey(Category, null=True, blank=True)
    
    # The subtype stores the lowest-level classname in the inheritence tree
    subtype = models.CharField(max_length=255, editable=False)
    
    objects = ProductManager()
    
    def save(self, *args, **kwargs):
        '''
        Saves the name of the subtype to the subtype column.
        '''
        self.subtype = self.__class__.__name__.lower()
        super(Product, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name
    
    def specify(self):
        '''
        This magic method returns this as an instance of the most specific
        decendant in the inheritence tree.
        '''
        return getattr(self, self.subtype, self)
    
    def get_price(self):
        '''
        Return the price for this item (provided for extensibility)
        '''
        return self.unit_price
    
    class Meta:
        app_label = 'shop'
        