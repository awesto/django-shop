#-*- coding: utf-8 -*-
from django import forms


class LocalizeDecimalFieldsMixin(object):
    '''
    To be used as a mixin for localizing DecimalField's in the admin interface. 
    '''
    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizeDecimalFieldsMixin, cls).__new__(cls)
        for field in new_class.base_fields.values():
            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True
        return new_class
