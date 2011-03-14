# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

class PayOnDeliveryBackend(object):
    
    backend_name = "Pay On Delivery"
    url_namespace = "pay-on-delivery"
    
    def __init__(self, shop):
        self.shop = shop # This is the shop reference, it allows this backend
        # to interact with it in a tidy way (look ma', no imports!)
            
    def simple_view(self, request):
        # Get the order object
        the_order = self.shop.get_order(request)
        # Set the payment method to be this backend (for traceability)
        self.shop.set_payment_method(the_order, self.backend_name)
        # Set it as payed (it needs to be payed to the delivery guy, we assume 
        # he does his job properly)
        self.shop.pay(the_order, the_order.order_total)
        # TODO: Needs a better view than this!
        return self.shop.finished()
        
    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.simple_view, name='pay-on-delivery' ),
        )
        return urlpatterns
    
