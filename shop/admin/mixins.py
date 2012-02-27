#-*- coding: utf-8 -*-
from django import forms


class LocalizeDecimalFieldsMixin(object):
    '''
    To be used as a mixin for classes derived from admin.ModelAdmin,
    admin.TabularInline, etc. which localizes the input fields for models of
    with type DecimalField in the admin interface.
    '''
    class LocalizeDecimalFieldsForm(forms.ModelForm):
        def __new__(cls, *args, **kwargs):
            new_class = super(LocalizeDecimalFieldsMixin.LocalizeDecimalFieldsForm, cls).__new__(cls)
            if hasattr(new_class, 'base_fields'):
                for field in new_class.base_fields.values():
                    if isinstance(field, forms.DecimalField):
                        field.localize = True
                        field.widget.is_localized = True
            return new_class

    form = LocalizeDecimalFieldsForm
