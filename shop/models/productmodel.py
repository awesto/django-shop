# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.signals import pre_save
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
    
    class Meta:
        verbose_name_plural = "categories"
        app_label = 'shop'
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])
    
    def get_products(self):
        '''
        Gets the products belonging to this category (not recursively)
        '''
        return Product.objects.filter(category=self)
    
    def get_child_categories(self):
        return Category.objects.filter(parent_category=self)

class ProductManager(models.Manager):
    
    def active(self):
        return self.filter(active=True)

class ProductMetaClass(ModelBase):
    '''
    Pretty much lifted from django.db.models.base.ModelBase
    
    Registers Product.save_subtype_name as a callback for the pre_save signal
    for all of the subclasses of Product.
    
    To understand it you might want to read about Python __metaclass__...
    '''
    def __new__(cls, name, bases, attrs):
        # That is - on a new "registration" (loading) of a subclass
        super_new = super(ProductMetaClass, cls).__new__ # The new class (not instance!)
        parents = [b for b in bases if isinstance(b, ProductMetaClass)]
        if not parents:
            # If this isn't a subclass of Product, don't do anything special.
            # This means it's a "pure" product
            return super_new(cls, name, bases, attrs)
        else:
            # This is a subclass of Product. Let's register it to pre_save
            super_klass = super_new(cls, name, bases,attrs)
            pre_save.connect(super_klass.save_subtype_name, sender=super_klass, weak=False)
            return super_klass

class Product(models.Model):
    '''
    A basic product for the shop
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property
    '''
    
    __metaclass__ = ProductMetaClass
    
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
    
    class Meta:
        app_label = 'shop'
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])
    
    def get_specific(self):
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
    
    def get_name(self):
        '''
        Return the name of this Product (provided for extensibility)
        '''
        return self.name
    
    @classmethod
    def save_subtype_name(cls, instance, **kwargs):
        '''
        This is called when a subclass of Product is saved. It sets the 
        relation name to the subclass in the "subtype" field of the Product 
        instance.
        This allows "get_specific()" to always return the specific instance of 
        the subclass, no matter its type.
        
        This method is (and should) only called from the pre_save signal set
        in ProductMetaClass
        '''
        instance.subtype = cls.__name__.lower()

class OptionGroup(models.Model):
    '''
    A logical group of options
    Example:
    
    "Colors"
    '''
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product)
    
    class Meta:
        app_label = 'shop'

class Option(models.Model):
    '''
    A product option. Examples:
    
    "Red": 10$
    "Blue": 5$
    ...
    '''
    name = models.CharField(max_length=255)
    price = CurrencyField() # Can be negative
    group = models.ForeignKey(OptionGroup)
    
    class Meta:
        app_label = 'shop'