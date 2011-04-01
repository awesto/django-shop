#-*- coding: utf-8 -*-
from shop.models.ordermodel import OrderExtraInfo
from shop.util.order import get_order_from_request

class BaseBackendAPI(object):
    '''
    A base-baseclass for shop APIs.
    
    Both payment and shipping backends need some common functions from the shop
    interface (for example get_order() is useful in both cases). To reduce code
    duplication, theses common methods are defined here and inherited by shop
    interfaces (DRY)
    
    Another approach would be to stuff everything here, but I think it opens
    up potential to overbloating this one class.
    This is debatable and relatively easy to change later anyway.
    
    Define all functions common to both the shipping and the payment shop APIs 
    here
    
    PLEASE: When adding functions here please write a short description of
    them in BaseShippingBackend and BasePaymentBackend, future implementers
    thank you :)
    '''
    def get_order(self, request):
        '''
        Returns the order object for the current shopper.
        
        This is called from the backend's views as: 
        >>> order = self.shop.getOrder(request)
        '''
        # it might seem a bit strange to simply forward the call to a helper, 
        # but this avoids exposing the shop's internal workings to module 
        # writers
        return get_order_from_request(request)
    
    def add_extra_info(self,order, text):
        '''
        Add an extra info text field to the order
        '''
        OrderExtraInfo.objects.create(text=text, order=self)
    
