# -*- coding: utf-8 -*-
from decimal import Decimal
from shop.cart.cart_modifiers_base import BaseCartModifier

class TenPercentGlobalTaxModifier(BaseCartModifier):
    '''
    A basic Tax calculator: it simply adds a taxes field to the *order*, 
    and makes it a fixed percentage of the subtotal (10%)
    
    Obviously, this is only provided as an example, and anything serious should
    use a more dynamic configuration system, such as settings or models to
    hold the tax values...
    '''
    
    TAX_PERCENTAGE = Decimal('10')
    
    def add_extra_cart_price_field(self, cart):
        '''
        Add a field on cart.extra_price_fields:
        '''
        taxes = (self.TAX_PERCENTAGE/100) * cart.subtotal_price
        to_append = ('Taxes total', taxes)
        cart.extra_price_fields.append(to_append)
        return cart
    
class TenPercentPerItemTaxModifier(BaseCartModifier):
    '''
    This adds a 10% tax cart modifier, calculated on the item's base price, plus
    any modifier applied to the cart item *so far* (order matters!).
    
    Make sure the moment you apply taxes comply with your local regulations!
    Some countries insist that taxes are calculated after/before discounts, and
    so forth
    '''
    TAX_PERCENTAGE = Decimal("10")
    
    def add_extra_cart_item_price_field(self, cart_item):
        total_before_taxes = Decimal('0')
        for label, value in cart_item.extra_price_fields:
            total_before_taxes = total_before_taxes + value
            
        tax_amount =(self.TAX_PERCENTAGE/100) * total_before_taxes
        
        to_append = ('Taxes (10%)', tax_amount)
        cart_item.extra_price_fields.append(to_append)