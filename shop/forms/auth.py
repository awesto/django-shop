# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model, authenticate, login, password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.forms import widgets, ModelForm
from django.template.loader import select_template
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from djng.forms import fields, NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm

from shop.conf import app_settings
from shop.models.customer import CustomerModel
from .base import UniqueEmailValidationMixin


class RegisterUserForm(NgModelFormMixin, NgFormValidationMixin, UniqueEmailValidationMixin, Bootstrap3ModelForm):
    form_name = 'register_user_form'
    scope_prefix = 'form_data'
    field_css_classes = 'input-group has-feedback'

    email = fields.EmailField(
        label=_("Your e-mail address"),
        widget=widgets.EmailInput(attrs={'placeholder': _("E-mail address")})
    )

    preset_password = fields.BooleanField(
        label=_("Preset password"),
        widget=widgets.CheckboxInput(),
        required=False,
        help_text=_("Send a randomly generated password to your e-mail address."),
    )

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = fields.CharField(
        label=_("New password"),
        widget=widgets.PasswordInput(attrs={'placeholder': _("Password")}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = fields.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=widgets.PasswordInput(attrs={'placeholder': _("Password")}),
        help_text=format_html('<ul><li>{}</li></ul>', _("Confirm the password.")),
    )

    class Meta:
        model = CustomerModel
        fields = ['email', 'password1', 'password2']

    def __init__(self, data=None, instance=None, *args, **kwargs):
        if data and data.get('preset_password', False):
            pwd_length = max(self.base_fields['password1'].min_length or 8, 8)
            password = get_user_model().objects.make_random_password(pwd_length)
            data['password1'] = data['password2'] = password
        super(RegisterUserForm, self).__init__(data=data, instance=instance, *args, **kwargs)

    def clean(self):
        cleaned_data = super(RegisterUserForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2)
        return cleaned_data

    def save(self, request=None, commit=True):
        self.instance.user.is_active = True
        self.instance.user.email = self.cleaned_data['email']
        self.instance.user.set_password(self.cleaned_data['password1'])
        self.instance.recognize_as_registered(request, commit=False)
        customer = super(RegisterUserForm, self).save(commit)
        password = self.cleaned_data['password1']
        if self.cleaned_data['preset_password']:
            self._send_password(request, customer.user, password)
        user = authenticate(username=customer.user.username, password=password)
        login(request, user)
        return customer

    def _send_password(self, request, user, password):
        current_site = get_current_site(request)
        context = {
            'site_name': current_site.name,
            'absolute_base_uri': request.build_absolute_uri('/'),
            'email': user.email,
            'password': password,
            'user': user,
        }
        subject = select_template([
            '{}/email/register-user-subject.txt'.format(app_settings.APP_LABEL),
            'shop/email/register-user-subject.txt',
        ]).render(context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = select_template([
            '{}/email/register-user-body.txt'.format(app_settings.APP_LABEL),
            'shop/email/register-user-body.txt',
        ]).render(context)
        user.email_user(subject, body)


class ContinueAsGuestForm(ModelForm):
    """
    Handles Customer's decision to order as guest.
    """
    form_name = 'continue_as_guest_form'
    scope_prefix = 'form_data'

    class Meta:
        model = CustomerModel
        fields = ()  # this form doesn't show any fields

    def save(self, request=None, commit=True):
        self.instance.recognize_as_guest(request, commit=False)
        self.instance.user.is_active = app_settings.GUEST_IS_ACTIVE_USER
        if self.instance.user.is_active:
            # set a usable password, otherwise the user later can not reset its password
            password = get_user_model().objects.make_random_password(length=30)
            self.instance.user.set_password(password)
        return super(ContinueAsGuestForm, self).save(commit)
