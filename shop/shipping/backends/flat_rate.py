# -*- coding: utf-8 -*-

from decimal import Decimal
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render_to_response

class FlatRateShipping(object):
    '''
    This is just an example of a possible flat-rate shipping module, that 
    charges a flat rate defined in settings.SHOP_SHIPPING_FLAT_RATE
    '''
    url_namespace = 'flat' 
    backend_name = 'Flat rate'
    
    def __init__(self, shop):
        self.shop = shop # This is the shop reference, it allows this backend
        # to interact with it in a tidy way (look ma', no imports!)
    
    def view_process_order(self,request):
        '''
        A simple (not class-based) view to process an order.
        
        This will be called by the selection view via the default url (that is
        registered on server load).
        The goal of this view is to 
        
        '''
        self.shop.add_shipping_costs(self.shop.get_order(request), 
                                     'Flat shipping',
                                     Decimal(settings.SHOP_SHIPPING_FLAT_RATE))
        return self.shop.finished() # That's an HttpResponseRedirect
    
    def view_display_fees(self,request):
        '''
        A simple, normal view that displays a template showing how much the 
        shipping will be (it's an example, alright)
        '''
        ctx = {}
        ctx.update({'shipping_costs':Decimal(settings.SHOP_SHIPPING_FLAT_RATE)})
        return render_to_response('shop/shipping/flat_rate/display_fees.html',ctx)
    
        
    def get_urls(self):
        '''
        Return the list of URLs defined here.
        '''
        urlpatterns = patterns('',
            url(r'^$', self.view_display_fees, name='flat'),
            url(r'^process/$', self.view_process_order, name='flat_process'),
        )
        return urlpatterns
        