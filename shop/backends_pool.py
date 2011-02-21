#-*- coding: utf-8 -*-
from django.conf import settings
from django.core import exceptions
from django.utils.importlib import import_module
from shop.payment.payment_backend_base import PaymentBackendAPI
from shop.shipping.shipping_backend_base import ShippingBackendAPI


class BackendsPool(object):
    USE_CACHE = True
    
    SHIPPING = 'SHOP_SHIPPING_BACKENDS'
    PAYMENT = 'SHOP_PAYMENT_BACKENDS'
    
    PAYMENT_SHOP_INTERFACE = PaymentBackendAPI()
    SHIPPING_SHOP_INTERFACE = ShippingBackendAPI()
    
    def __init__(self):
        self._payment_backends_list = []
        self._shippment_backends_list = []

    def get_payment_backends_list(self):
        '''
        Returns the list of payment backends, as instances, from the list of 
        backends defined in settings.SHOP_PAYMENT_BACKENDS
        '''
        if self._payment_backends_list and self.USE_CACHE:
            return self._payment_backends_list
        else:
            self._payment_backends_list = self._load_backends_list(self.PAYMENT,
                                            self.PAYMENT_SHOP_INTERFACE)
            return self._payment_backends_list
    
    def get_shipping_backends_list(self):
        '''
        Returns the list of payment backends, as instances, from the list of 
        backends defined in settings.SHOP_SHIPPING_BACKENDS
        '''
        if self._shippment_backends_list and self.USE_CACHE:
            return self._shippment_backends_list
        else:
            self._shippment_backends_list = self._load_backends_list(self.SHIPPING,
                                            self.SHIPPING_SHOP_INTERFACE)
            return self._shippment_backends_list
            
    def _check_backend_for_validity(self, backend_instance):
        '''
        This enforces having a valid name and url namespace defined.
        Backends, both shipping and payment are namespaced in respectively
        /pay/ and /ship/ URL spaces, so as to avoid name clashes.
        
        "Namespaces are one honking great idea -- let's do more of those!"
        '''
        backend_name = getattr(backend_instance, 'backend_name', "")
        if backend_name == "":
            raise NotImplementedError(
            'One of your backends lacks a name, please define one.')
            
        url_namespace = getattr(backend_instance, 'url_namespace', "")
        if url_namespace == "":
            raise NotImplementedError(
                'Please set a namespace for backend "%s"' % backend_instance.backend_name)
        
    def _load_backends_list(self, setting_name, shop_object):
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
            
            # Seems like it is a real class - let's instanciate it!
            # This is where the backends receive their self.shop reference!
            mod_instance = mod_class(shop=shop_object)
            
            self._check_backend_for_validity(mod_instance)
            
            # The backend seems valid (nothing raised), let's add it to the 
            # return list.
            result.append(mod_instance)
            
        return result

backends_pool = BackendsPool()