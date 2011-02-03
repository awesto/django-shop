# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.prices.price_modifiers_base import BasePriceModifier

class TaxPercentageModifier(BasePriceModifier):
    '''
    A basic Tax calculator: it simply adds a taxes field to the order, 
    and makes it a fixed percentage of the subtotal.
    
    Obviously, this will have to be put in a setting later, but for now
    it will just be a constant.
    '''
    
    TAX_PERCENTAGE = Decimal('7.6') # That's VAT
    
    def add_extra_cart_price_field(self, cart):
        '''
        Add a field on cart.extra_price_fields:
        
        >>> cart.extra_price_fields.update({'Taxes total': 19.00})
        '''
        taxes = (self.TAX_PERCENTAGE/100) * cart.subtotal_price
        cart.extra_price_fields.update({'Taxes total':taxes})
        return cart