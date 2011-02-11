# -*- coding: utf-8 -*-

'''
This file defines the interafces one should implement when either creating a new
payment module or willing to use modules with another shop system.
'''
from shop.backend_base import BaseBackendAPI, BaseBackend

class PaymentBackendAPI(BaseBackendAPI):
    '''
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    payment plugins are interchangeable between systems.
    
    This implementation is the interface reference for Django Shop
    
    '''
    
    def setOrderFinished(self):
        '''
        Sets the current order processing status to "Finished"
        '''

class BasePaymentBackend(BaseBackend):
    '''
    This is the base class for all payment backends to implement.
    
    The goal is to be able to register a few payment modules, and let one of 
    them be selected at runtime by the shopper.
    '''
    
    url_namespace = "" # That's what part of the URL goes after "pay/"
    backend_name = ""
    shop = None # Must be injected at __init__()
    
    def __init__(self, shop=PaymentBackendAPI()):
        '''
        Make sure the shop helper is of the right type, then call super()
        '''
        self.shop = shop
        super(BasePaymentBackend, self).__init__()
        
    def get_urls(self):
        '''
        Return a set of patterns() or urls() to hook to the site's main url
        resolver.
        This allows payment systems to register urls for callback, or to 
        maintain a set of own views / templates
        '''