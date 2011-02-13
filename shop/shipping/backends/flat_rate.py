# -*- coding: utf-8 -*-

from decimal import Decimal
from django.conf import settings
from shop.shipping.shipping_backend_base import BaseShippingBackend

class FlatRateShipping(BaseShippingBackend):
    '''
    This is just an example of a possible flat-rate shipping module, that 
    charges a flat rate defined in settings.SHOP_SHIPPING_FLAT_RATE
    '''
    
    def process_order(self,order):
        self.shop.add_shipping_costs(self.shop.get_order(), 
                                     'Flat shipping',
                                     Decimal(settings.SHOP_SHIPPING_FLAT_RATE))
        