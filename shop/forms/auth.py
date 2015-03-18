# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3ModelForm


class CustomerForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    scope_prefix = 'data.customer'
    form_name = 'customer_form'

    class Meta:
        model = get_user_model()
        exclude = ('username', 'password', 'last_login', 'is_superuser', 'is_staff', 'is_active',
            'groups', 'user_permissions', 'date_joined',)

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
