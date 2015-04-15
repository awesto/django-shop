# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3ModelForm
from shop.models.auth import get_customer


class RegisterForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    identifier = 'register_user'
    scope_prefix = 'data.register_user'
    form_name = 'register_user_form'

    password1 = fields.CharField(label=_("Choose a password"), widget=widgets.PasswordInput,
                                 min_length=6, help_text=_("Minimum length is 6 characters"))
    password2 = fields.CharField(label=_("Repeat password"), widget=widgets.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2',)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            msg = _("Passwords do not match")
            raise ValidationError(msg)
        return cleaned_data

    @classmethod
    def form_factory(cls, request, data, cart):
        user = get_customer(request)
        customer_form = cls(data=data, instance=user)
        if customer_form.is_valid():
            customer_form.save()
        else:
            return {cls.form_name: customer_form.errors}
