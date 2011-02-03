# -*- coding: utf-8 -*-
from django.db.models.fields import DecimalField


class CurrencyField(DecimalField):
    '''
    A CurrencyField is simply a subclass of DecimalField with a fixed format:
    max_digits = 12, decimal_places=2, and defaults to 0.00
    '''
    def __init__(self, **kwargs):
        if kwargs.get('max_digits'):
            delattr(kwargs,'max_digits')
        if kwargs.get('decimal_places'):
            delattr(kwargs,'decimal_places')
        default = kwargs.get('default', '0.00') # get "default" or 0.00
        if kwargs.get('default'):
            delattr(kwargs,'default')
        return super(CurrencyField,self).__init__(max_digits=12,decimal_places=2,default=default,**kwargs)