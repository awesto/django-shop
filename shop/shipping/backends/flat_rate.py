'''
Created on Jan 17, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''

from django.conf import settings
from shipping.shipping_backend_base import BaseShippingBackend

class FlatRateShipping(BaseShippingBackend):
    '''
    This is just an example of a possible flat-rate shipping module, that 
    charges a flat rate defined in settings.SHOP_SHIPPING_FLAT_RATE
    '''
    def process_order(self,order):
        order.shipping_cost = settings.SHOP_SHIPPING_FLAT_RATE