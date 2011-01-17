'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from django.db import models

class Order(models.Model):
    '''
    A model representing an Order.
    
    An order is the "in process" counterpart of the shopping cart, which holds
    stuff like the shipping and billing addresses (copied from the User profile)
    when the Order is first created), list of items, and holds stuff like the
    status, shipping costs, taxes, etc...
    '''
    
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Addresses MUST be copied over to the order when it's created.
    shipping_name = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255)
    shipping_zip_code = models.CharField(max_length=20)
    shipping_state = models.CharField(max_length=255)
    shipping_country = models.CharField(max_length=255)
    
    billing_name = models.CharField(max_length=255)
    billingaddress = models.CharField(max_length=255)
    billing_address2 = models.CharField(max_length=255)
    billing_zip_code = models.CharField(max_length=20)
    billing_state = models.CharField(max_length=255)
    billing_country = models.CharField(max_length=255)

class OrderItem():
    pass
    