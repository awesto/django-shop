'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from django.contrib.auth.models import User
from django.db import models
from models.productmodel import Product

class Cart(models.Model):
    '''
    This should be a rather simple list of items. Ideally it should be bound to
    a session and not to a User is we want to let people buy from our shop 
    without having to register with us.
    '''
    user = models.ForeignKey(User)
    
    def add_product(self,product):
        '''
        Adds a product to the cart
        '''
        # Let's see if we already have an Item with the same product ID
        if len(CartItem.filter(cart=self).filter(product=product)) > 0:
            cart_item = CartItem.filter(cart=self).filter(product=product)[0]
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(cart=self,quantity=1,product=product)
            cart_item.save()
    
class CartItem(models.Model):
    '''
    This is a holder for the quantity of items in the cart and, obviously, a 
    pointer to the actual Product being purchased :)
    '''
    cart = models.ForeignKey(Cart, related_name="items")
    
    quatity = models.IntegerField()
    product = models.ForeignKey(Product)