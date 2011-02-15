# -*- coding: utf-8 -*-

from decimal import Decimal
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from shop.shipping.shipping_backend_base import BaseShippingBackend

class FlatRateShipping(BaseShippingBackend):
    '''
    This is just an example of a possible flat-rate shipping module, that 
    charges a flat rate defined in settings.SHOP_SHIPPING_FLAT_RATE
    '''
    url_namespace = 'flat' 
    backend_name = 'Flat rate'
    
    def process_order(self,request):
        '''
        A simple (not class-based) view to process an order.
        
        This will be called by the selection view via the default url (that is
        registered on server load).
        The goal of this view is to 
        
        '''
        self.shop.add_shipping_costs(self.shop.get_order(request), 
                                     'Flat shipping',
                                     Decimal(settings.SHOP_SHIPPING_FLAT_RATE))
        return self.finished() # That's an HttpResponseRedirect
    
        
    def get_urls(self):
        '''
        Return the list of URLs defined here.
        '''
        urlpatterns = patterns('',
            url(r'^$', self.process_order, name='flat'),
        )
        return urlpatterns
        