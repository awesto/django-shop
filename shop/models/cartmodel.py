# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from shop.cart.modifiers_pool import cart_modifiers_pool
from shop.models.productmodel import Product

class Cart(models.Model):
    '''
    This should be a rather simple list of items. Ideally it should be bound to
    a session and not to a User is we want to let people buy from our shop 
    without having to register with us.
    '''
    # If the user is null, that means this is used for a session
    user = models.OneToOneField(User, null=True, blank=True)
    
    extra_price_fields = {} # That will hold things like tax totals or total discount
    subtotal_price = Decimal('0.0') 
    total_price = Decimal('0.0')
    
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'shop'
    
    def __init__(self, *args, **kwargs):
        super(Cart, self).__init__(*args,**kwargs)
        self.update() # This populates transient fields when coming from the DB
    
    def add_product(self,product, quantity=1):
        '''
        Adds a product to the cart
        '''
        # Let's see if we already have an Item with the same product ID
        if len(CartItem.objects.filter(cart=self).filter(product=product)) > 0:
            cart_item = CartItem.objects.filter(cart=self).filter(product=product)[0]
            cart_item.quantity = cart_item.quantity + int(quantity)
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(cart=self,quantity=quantity,product=product)
            cart_item.save()
            
        self.save() # to get the last updated timestamp
            
    def update(self):
        '''
        This should be called whenever anything is changed in the cart (added or removed)
        It will loop on all line items in the cart, and call all the price modifiers
        on each row.
        After doing this, it will compute and update the order's total and
        subtotal fields, along with any payment field added along the way by
        modifiers.
        
        Note that theses added fields are not stored - we actually want to reflect
        rebate and tax changes on the *cart* items, but we don't want that for
        the order items (since they are legally binding after the "purchase" button
        was pressed)
        '''
        items = CartItem.objects.filter(cart=self)
        
        self.subtotal_price = Decimal('0.0') # Reset the subtotal
        
        for item in items: # For each OrderItem (order line)...
            self.subtotal_price = self.subtotal_price + item.update()
            item.save()
        
        # Now we have to iterate over the registered modifiers again (unfortunately)
        # to pass them the whole Order this time
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.process_cart(self)
            
        self.total_price = self.subtotal_price
        # Like for line items, most of the modifiers will simply add a field
        # to extra_price_fields, let's update the total with them
        for value in self.extra_price_fields.itervalues():
            self.total_price = self.total_price + value            
        
    
class CartItem(models.Model):
    '''
    This is a holder for the quantity of items in the cart and, obviously, a 
    pointer to the actual Product being purchased :)
    '''
    cart = models.ForeignKey(Cart, related_name="items")
    
    # These must not be stored, since their components can be changed between
    # sessions / logins etc...
    line_subtotal = Decimal('0.0') 
    line_total = Decimal('0.0') 
    extra_price_fields = {} # That will hold extra fields to display to the user (ex. taxes, discount)
    
    quantity = models.IntegerField()
    
    product = models.ForeignKey(Product)
    
    class Meta:
        app_label = 'shop'
    
    def update(self):
        self.line_subtotal = self.product.get_price() * self.quantity
        self.line_total = self.line_subtotal
        
        for modifier in cart_modifiers_pool.get_modifiers_list():
            # We now loop over every registered price modifier,
            # most of them will simply add a field to extra_payment_fields
            modifier.process_cart_item(self)
            for value in self.extra_price_fields.itervalues():
                self.line_total = self.line_total + value
                
        return self.line_total
