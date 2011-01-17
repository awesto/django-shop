'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from django.db import models
from models.productmodel import Product

class Cart(models.Model):
    '''
    This should be a rather simple list of items. Ideally it should be bound to
    a session and not to a User is we want to let people buy from our shop 
    without having to register with us.
    '''
    
class Cartitem(models.Model):
    '''
    This is a holder for the quantity of items in the cart and, obviously, a 
    pointer to the actual Product being purchased :)
    '''
    quatity = models.IntegerField()
    product = models.ForeignKey(Product)