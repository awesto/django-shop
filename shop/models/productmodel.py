# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel
from shop.util.fields import CurrencyField


class ProductManager(PolymorphicManager):
    
    def active(self):
        return self.filter(active=True)

class Product(PolymorphicModel):
    """
    A basic product for the shop
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property
    """
    
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    short_description = models.CharField(max_length=255)
    long_description = models.TextField()
    active = models.BooleanField(default=False)
    
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    unit_price = CurrencyField()
    
    objects = ProductManager()
    
    class Meta:
        app_label = 'shop'
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])
    
    def get_price(self):
        """
        Return the price for this item (provided for extensibility)
        """
        return self.unit_price
    
    def get_name(self):
        """
        Return the name of this Product (provided for extensibility)
        """
        return self.name
    
