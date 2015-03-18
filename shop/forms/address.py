# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3ModelForm
from shop.models.address import AddressModel


class AddressForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    default_field_css_classes = getattr(Bootstrap3ModelForm, 'field_css_classes')
    field_css_classes = {
        '*': default_field_css_classes,
        'zip_code': ['form-group', 'frmgrp-zip_code'],
        'location': 'form-group frmgrp-location',
    }

    class Meta:
        model = AddressModel
        exclude = ('user', 'priority_shipping', 'priority_invoice',)

    def __init__(self, addr_type, *args, **kwargs):
        kwargs.update(scope_prefix='data.{}_address'.format(addr_type),
                      form_name='{}_addr_form'.format(addr_type))
        super(AddressForm, self).__init__(*args, **kwargs)
