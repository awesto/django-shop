#-*- coding: utf-8 -*-
from django import forms


class LocalizeDecimalFieldsForm(forms.ModelForm):
    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizeDecimalFieldsForm, cls).__new__(cls)
        if hasattr(new_class, 'base_fields'):
            for field in new_class.base_fields.values():
                if isinstance(field, (forms.DecimalField, forms.FloatField)):
                    field.localize = True
                    field.widget.is_localized = True
        return new_class


class LocalizeDecimalFieldsMixin(object):
    '''
    To be used as a mixin for classes derived from admin.ModelAdmin,
    admin.TabularInline, etc. which localizes the input fields for models
    of type DecimalField in the admin interface.
    If your class derived from ModelAdmin wants to override the form attribute,
    make sure that this form is derived from LocalizeDecimalFieldsForm and not
    from forms.ModelForm.
    '''
    form = LocalizeDecimalFieldsForm
