# -*- coding: utf-8 -*-

class BaseCartModifier(object):
    '''
    Price modifiers are the cart's counterpart to backends.
    It allows to implement Taxes and rebates / bulk prices in an elegant manner:
    
    Everytime the cart is refreshed (via it's update() method), the cart will 
    call all subclasses of this registered with their full path in the
    settings.SHOP_PRICE_MODIFIERS setting.
    '''
        
    def process_cart_item(self, cart_item):
        '''
        This will be called for every line item in the Cart:
        Line items typically contain: product, unit_price, quantity...
        
        Subtotal for every line (unit price * quantity) is already computed, but
        the line total is 0, and is expected to be calculated in the Cart's 
        update() method
        '''
        return self.add_extra_cart_item_price_field(cart_item)
    
    def process_cart(self, cart):
        '''
        This will be called once per Cart, after every line item was treated
        The subtotal for the cart is already known, but the Total is 0.
        Like for the line items, total is expected to be calculated in the cart's
        update() method.
        
        Line items should be complete by now, so all of their fields are accessible
        '''
        return self.add_extra_cart_price_field(cart)
    
    def add_extra_cart_item_price_field(self, cart_item):
        '''
        Add an extra price field on cart_item.extra_price_fields:
        
        This allows to modify the price easily, simply add a 
        {'Label':Decimal(difference)} entry to it.
        
        A tax modifier would do something like this:
        >>> cart_item.extra_price_fields.update({'taxes': Decimal(9)})
        
        And a rebate modifier would do something along the lines of:
        >>> cart_item.extra_price_fields.update({'rebate': Decimal(-9)})
        
        More examples can be found in shop.cart.modifiers.*
        
        '''
        return cart_item # Does nothing by default
    
    def add_extra_cart_price_field(self, cart):
        '''
        Add a field on cart.extra_price_fields:
        
        In a similar fashion, this allows to easily add price modifications to 
        the general Cart object, 
        
        >>> cart.extra_price_fields.update({'Taxes total': 19.00})
        '''
        return cart