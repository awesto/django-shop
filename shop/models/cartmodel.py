# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from shop.prices.modifiers_pool import price_modifiers_pool
from shop.models.productmodel import Product
from shop.util.fields import CurrencyField

class Cart(models.Model):
    '''
    This should be a rather simple list of items. Ideally it should be bound to
    a sessin and not to a User is we want to let people buy from our shop 
    without having to register with us.
    '''
    user = models.ForeignKey(User)
    
    extra_price_fields = {} # That will hold things like tax totals or total discount
    
    subtotal_price = CurrencyField()
    total_price = CurrencyField()
    
    def add_product(self,product):
        '''
        Adds a product to the cart
        '''
        # Let's see if we already have an Item with the same product ID
        if len(CartItem.objects.filter(cart=self).filter(product=product)) > 0:
            cart_item = CartItem.objects.filter(cart=self).filter(product=product)[0]
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(cart=self,quantity=1,product=product)
            cart_item.save()
            
    def update(self):
        '''
        This should be called whenever anything is changed in the cart (added or removed)
        '''
        items = list(CartItem.objects.filter(cart=self)) # force query to "cache" it
        
        self.subtotal_price = Decimal('0.0')
        for item in items:
            
            item.line_subtotal = item.product.base_price * item.quantity
            item.line_total = item.line_subtotal
            
            for modifier in price_modifiers_pool.get_modifiers_list():
                item = modifier.process_cart_item(item)
                for value in item.extra_price_fields.itervalues():
                    item.line_total = item.line_total + value
                    
            self.subtotal_price = self.subtotal_price + item.line_total
            item.save()
        
        for modifier in price_modifiers_pool.get_modifiers_list():
            modifier.process_cart(self)
            
        self.total_price = self.subtotal_price
        for value in self.extra_price_fields.itervalues():
            self.total_price = self.total_price + value
            
        self.save()
        
    class Meta:
        app_label = 'shop'
    
class CartItem(models.Model):
    '''
    This is a holder for the quantity of items in the cart and, obviously, a 
    pointer to the actual Product being purchased :)
    '''
    cart = models.ForeignKey(Cart, related_name="items")
    
    line_subtotal = CurrencyField()
    line_total = CurrencyField()
    
    extra_price_fields = {} # That will hold extra fields to display to the user (ex. taxes, discount)
    
    quantity = models.IntegerField()
    product = models.ForeignKey(Product)
    
    class Meta:
        app_label = 'shop'