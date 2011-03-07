#-*- coding: utf-8 -*-
from decimal import Decimal
from shop.cart.cart_modifiers_base import BaseCartModifier

class BulkRebateModifier(BaseCartModifier):
    
    def add_extra_cart_item_price_field(self, cart_item):
        '''
        Add a rebate to a line item depending on the quantity ordered:
        
        This serves as an example mass rebate modifier: if you buy more than
        5 items of the same kind, you get 10% off the bunch
        
        >>> cart_item.extra_price_fields.update({'Rebate': Decimal('10.0')})
        '''
        REBATE_PERCENTAGE = Decimal('10')
        NUMBER_OF_ITEMS_TO_TRIGGER_REBATE = 5
        if cart_item.quantity >= NUMBER_OF_ITEMS_TO_TRIGGER_REBATE:
            rebate = (REBATE_PERCENTAGE/100) * cart_item.line_subtotal
            to_append = ('Rebate', -rebate)
            cart_item.extra_price_fields.append(to_append)
        return cart_item