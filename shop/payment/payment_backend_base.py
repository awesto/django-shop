# -*- coding: utf-8 -*-

class BasePaymentBackend(object):
    '''
    This is the base class for all payment backends to implement.
    
    The goal is to be able to register a few payment modules, and let one of 
    them be selected at runtime by the shopper.
    '''
    def process_order(self,order):
        '''
        Processes payment for the supplied Order:
        
        Gather all necessary information from the Order object, and
        pass them to the payment backend (Paypal, whatever)
        '''
        
    def get_urls(self):
        '''
        Return a set of patterns() or urls() to hook to the site's main url
        resolver.
        This allows payment systems to register urls for callback, or to 
        maintain a set of own views / templates
        '''