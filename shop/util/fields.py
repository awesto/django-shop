'''
Created on Jan 18, 2011

@author: Christopher Glass <christopher.glass@divio.ch>
'''
from django.db.models.fields import DecimalField


class CurrencyField(DecimalField):
    '''
    A CurrencyField is simply a subclass of DecimalField with a fixed format:
    max_digits = 12 and decimal_places=2
    '''
    def __init__(self, **kwargs):
        if kwargs.get('max_digits'):
            del kwargs['max_digits']
        if kwargs.get('decimal_places'):
            del kwargs['decimal_places']
        return super(CurrencyField,self).__init__(max_digits=12,decimal_places=2,**kwargs)