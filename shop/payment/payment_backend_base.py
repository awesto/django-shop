# -*- coding: utf-8 -*-

'''
This file defines the interafces one should implement when either creating a new
payment module or willing to use modules with another shop system.
'''
from decimal import Decimal
from shop.backend_base import BaseBackendAPI, BaseBackend

class PaymentBackendAPI(BaseBackendAPI):
    '''
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    payment plugins are interchangeable between systems.
    
    This implementation is the interface reference for Django Shop
    
    Methods defined in BaseBackendAPI:
    getOrder(request): Return the Order object for the current shopper
    
    '''
    
    def pay(self, order, amount, save=True):
        '''
        "Pays" the specified amount for the given order.
        This allows to hook in more complex behaviors (like saving a history
        of payments in a Payment model)
        The optional save argument allows backends to explicitly not save the 
        order yet
        '''
        # TODO: Add a "Payment" model to handle this in a more professional way
        
        amount = Decimal(amount) # In case it's not already a Decimal
        order.amount_payed = order.amount_payed + amount
        if save:
            order.save()
        
    def set_payment_method(self, order, method, save=True):
        '''
        Sets the payment method on the order object to whatever is specified in
        the method argument (should be a String)
        '''
        order.payment_method = method
        if save:
            order.save()
        
class BasePaymentBackend(BaseBackend):
    '''
    This is the base class for all payment backends to implement.
    
    The goal is to be able to register a few payment modules, and let one of 
    them be selected at runtime by the shopper.
    
    Class members:
    
    url_namespace 
    backend_name
    shop
    '''
    
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