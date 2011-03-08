#-*- coding: utf-8 -*-
from django.conf import settings
from django.core import exceptions
from django.utils.importlib import import_module
from shop.models.ordermodel import OrderExtraInfo
from shop.util.order import get_order_from_request


class BaseBackendAPI(object):
    '''
    A base-baseclass for shop APIs.
    
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
        
class BaseBackend(object):
    '''
    A base-baseclass for all backends (payment backends and shipping backends)
    '''
    
    url_namespace = "" # That's what part of the URL goes after "pay/"
    backend_name = ""
    shop = None # Must be injected at __init__()
    
    def __init__(self):
        '''
        This enforces having a valid name and url namespace defined.
        Backends, both shipping and payment are namespaced in respectively
        /pay/ and /ship/ URL spaces, so as to avoid name clashes.
        
        "Namespaces are one honking great idea -- let's do more of those!"
        '''
        if self.backend_name == "":
            raise NotImplementedError(
                'One of your backends lacks a name, please define one.')
        if self.url_namespace == "":
            raise NotImplementedError(
                'Please set a namespace for backend "%s"' % self.backend_name)
            
class BackendsPool(object):
    USE_CACHE = True
    
    SHIPPING = 'SHOP_SHIPPING_BACKENDS'
    PAYMENT = 'SHOP_PAYMENT_BACKENDS'
    
    def __init__(self):
        self._payment_backends_list = []
        self._shippment_backends_list = []

    def get_payment_backends_list(self):
        if self._payment_backends_list and self.USE_CACHE:
            return self._payment_backends_list
        else:
            self._payment_backends_list = self._load_backends_list(self.PAYMENT)
            return self._payment_backends_list
    
    def get_shipping_backends_list(self):
        if self._shippment_backends_list and self.USE_CACHE:
            return self._shippment_backends_list
        else:
            self._shippment_backends_list = self._load_backends_list(self.SHIPPING)
            return self._shippment_backends_list
            
    def _load_backends_list(self, setting_name):
        result = []
        if not getattr(settings,setting_name, None):
            return result
        
        for backend_path in getattr(settings,setting_name, None):
            try:
                back_module, back_classname = backend_path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured(
                    '%s isn\'t a backend module. Check your %s setting' 
                    % (backend_path,setting_name))
            try:
                mod = import_module(back_module)
            except ImportError, e:
                raise exceptions.ImproperlyConfigured(
                        'Error importing backend %s: "%s". Check your %s setting' 
                        % (back_module, e, setting_name))
            try:
                mod_class = getattr(mod, back_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured(
                    'Backend module "%s" does not define a "%s" class. Check your %s setting' 
                    % (back_module, back_classname, setting_name))
                
            mod_instance = mod_class()
            result.append(mod_instance)
            
        return result

backends_pool = BackendsPool()