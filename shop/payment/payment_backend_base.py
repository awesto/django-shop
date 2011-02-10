# -*- coding: utf-8 -*-

'''
This file defines the interafces one should implement when either creating a new
payment module or willing to use modules with another shop system.
'''
from shop.models.ordermodel import Order

class PaymentBackendAPI(object):
    '''
    This object's purpose is to expose an API to the shop system.
    Ideally, shops (Django shop or others) should implement this API, so that
    payment plugins are interchangeable between systems.
    
    This implementation is the interface reference for Django Shop
    
    '''
    def getOrder(self, request):
        '''
        Returns the order object for the current shopper.
        
        This is called from the backend's views as: 
        >>> order = self.shop.getOrder(request)
        '''
        user = request.user
        order = Order.objects.filter(user=user).filter(status=Order.CONFIRMED)
        return order
    
    def setOrderFinished(self):
        '''
        Sets the current order processing status to "Finished"
        '''

class BasePaymentBackend(object):
    '''
    This is the base class for all payment backends to implement.
    
    The goal is to be able to register a few payment modules, and let one of 
    them be selected at runtime by the shopper.
    '''
    
    url_namespace = "" # That's what part of the URL goes after "pay/"
    backend_name = ""
    shop = PaymentBackendAPI() # That's the easier to use API
    
    def __init__(self):
        '''
        This enforces having a valid name and url namespace defined.
        '''
        if self.backend_name == "":
            raise NotImplementedError(
                'One of your payment backends lacks a name, please define one.')
        if self.url_namespace == "":
            raise NotImplementedError(
                'Please set a namespace for backend "%s"' % self.backend_name)
        
    def get_urls(self):
        '''
        Return a set of patterns() or urls() to hook to the site's main url
        resolver.
        This allows payment systems to register urls for callback, or to 
        maintain a set of own views / templates
        '''