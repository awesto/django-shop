# -*- coding: utf-8 -*-
from shop.backend_base import BaseBackendAPI, BaseBackend

class ShippingBackendAPI(BaseBackendAPI):
    '''
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    shipping plugins are interchangeable between systems.
    
    This implementation is the interface reference for Django Shop
    
    Methods defined in BaseBackendAPI:
    getOrder(request): Return the Order object for the current shopper
    '''

class BaseShippingBackend(BaseBackend):
    
    def __init__(self, shop=ShippingBackendAPI()):
        '''
        Make sure the shop helper is of the right type (shipping), then call 
        super
        '''
        self.shop = shop
        super(BaseShippingBackend, self).__init__()
        
    def process_order(self,order):
        '''
        Processes the supplied Order object for shipping costs computing.
        This should ideally store the shipping costs total in 
        Order.shipping_cost.
        
        '''
        
    def process_order_item(self,order_item):
        '''
        Processes the supplied Order object for shipping costs computing.
        This should ideally store the shipping costs total in 
        Order.shipping_cost.
        
        '''