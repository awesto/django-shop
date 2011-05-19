# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel
from shop.util.fields import CurrencyField
from django.db.models import Count


class ProductStatisticsManager(PolymorphicManager):
    """
    A Manager for all the non-object manipulation needs, mostly statistics and
    other "data-mining" toys.
    """
    
    def top_selling_products(self, quantity):
        """
        This method "mines" the previously passed orders, and gets a list of
        products (of a size equal to the quantity parameter), ordered by how 
        many times they have been purchased.
        """
        # Importing here is fugly, but it saves us from circular imports...
        from shop.models.ordermodel import OrderItem
        # Get an aggregate of product references and their respective counts
        top_products_data = OrderItem.objects.values(
                'product_reference').annotate(
                    product_count=Count('product_reference')
                ).order_by('product_count'
            )[:quantity]

        # The top_products_data result should be in the form:
        # [{'product_reference': '<product_id>', 'product_count': <count>}, ...]
 
        top_products_list = [] # The actual list of products
        for values in top_products_data:
            prod = Product.objects.get(pk=values.get('product_reference'))
            # We could eventually return the count easily here, if needed.
            top_products_list.append(prod)

        return top_products_list

class ProductManager(PolymorphicManager):
    """
    A more classic manager for Product filtering and manipulation.
    """
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
    active = models.BooleanField(default=False)
    
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    unit_price = CurrencyField()
    
    # Managers
    objects = ProductManager()
    statistics = ProductStatisticsManager()
    
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
    
