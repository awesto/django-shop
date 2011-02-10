#-*- coding: utf-8 -*-
from django.conf import settings
from django.core import exceptions
from django.utils.importlib import import_module


class PaymentBackendsPool(object):
    USE_CACHE = True
    
    def __init__(self):
        self._backends_list = []

    def get_backends_list(self):
        if self._backends_list and self.USE_CACHE:
            return self._backends_list
        else:
            self._backends_list = self._load_backends_list()
            return self._backends_list
            
    def _load_backends_list(self):
        result = []
        if not getattr(settings,'SHOP_PAYMENT_BACKENDS', None):
            return result
        
        for backend_path in settings.SHOP_PAYMENT_BACKENDS:
            try:
                back_module, back_classname = backend_path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured(
                        '%s isn\'t a payment backend module' % backend_path)
            try:
                mod = import_module(back_module)
            except ImportError, e:
                raise exceptions.ImproperlyConfigured(
                        'Error importing backend %s: "%s"' % (back_module, e))
            try:
                mod_class = getattr(mod, back_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured(
                    'Payment Backend module "%s" does not define a "%s" class' 
                    % (back_module, back_classname))
                
            mod_instance = mod_class()
            result.append(mod_instance)
            
        return result

payment_backends_pool = PaymentBackendsPool()