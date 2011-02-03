#-*- coding: utf-8 -*-
from decimal import Decimal
from shop.prices.price_modifiers_base import BasePriceModifier

class BulkRebateModifier(BasePriceModifier):
    
    def add_extra_cart_item_price_field(self, cart_item):
        '''
        Add a field on cart_item.extra_price_fields:
        
        >>> cart_item.extra_price_fields.update({'taxes': 9.00})
        '''
        REBATE_PERCENTAGE = Decimal('10')
        NUMBER_OF_ITEMS_TO_TRIGGER_REBATE = 5
        if cart_item.quantity >= NUMBER_OF_ITEMS_TO_TRIGGER_REBATE:
            rebate = (REBATE_PERCENTAGE/100) * cart_item.line_subtotal
            cart_item.extra_price_fields.update({'Rebate': -rebate})
        return cart_item