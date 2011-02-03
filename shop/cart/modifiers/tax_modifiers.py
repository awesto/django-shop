# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.cart.cart_modifiers_base import BaseCartModifier

class TenPercentTaxModifier(BaseCartModifier):
    '''
    A basic Tax calculator: it simply adds a taxes field to the order, 
    and makes it a fixed percentage of the subtotal (10%)
    
    Obviously, this is only provided as an example, and anything serious should
    use a more dynamic configuration system, such as settings or models to
    hold the tax values.
    '''
    
    TAX_PERCENTAGE = Decimal('10') # That's VAT
    
    def add_extra_cart_price_field(self, cart):
        '''
        Add a field on cart.extra_price_fields:
        
        >>> cart.extra_price_fields.update({'Taxes total': 19.00})
        '''
        taxes = (self.TAX_PERCENTAGE/100) * cart.subtotal_price
        cart.extra_price_fields.update({'Taxes total':taxes})
        return cart