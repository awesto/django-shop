# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel
from shop.util.fields import CurrencyField
from django.utils.translation import ugettext_lazy as _

class ProductManager(PolymorphicManager):
    
    def active(self):
        return self.filter(active=True)

class Product(PolymorphicModel):
    """
    A basic product for the shop
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property
    """
    
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'))
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date added'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))
    
    unit_price = CurrencyField(verbose_name=_('Unit price'))
    
    objects = ProductManager()
    
    class Meta(object):
        app_label = 'shop'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    
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
    
