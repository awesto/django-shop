# -*- coding: utf-8 -*-

class BasePriceModifier():
    '''
    Price modifiers are the cart's counterpart to backends.
    It allows to implement Taxes and rebates / bulk prices in an elegant manner
    '''
    def process_cart(self, cart):
        return self.add_extra_cart_price_field(cart)
        
    def process_cart_item(self, cart_item):
        '''
        Do something fancy here, like calculate size of items or whatever
        '''
        return self.add_extra_cart_item_price_field(cart_item)
    
    def add_extra_cart_item_price_field(self, cart_item):
        '''
        Add a field on cart_item.extra_price_fields:
        
        >>> cart_item.extra_price_fields.update({'taxes': 9.00})
        '''
        return cart_item
    
    def add_extra_cart_price_field(self, cart):
        '''
        Add a field on cart.extra_price_fields:
        
        >>> cart.extra_price_fields.update({'Taxes total': 19.00})
        '''
        return cart