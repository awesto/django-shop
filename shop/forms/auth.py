# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.forms import widgets, ModelForm
from django.template.loader import get_template, select_template, render_to_string
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from djng.forms import fields, NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3ModelForm
from post_office import mail as post_office_mail
from post_office.models import EmailTemplate
from shop.conf import app_settings
from shop.forms.base import UniqueEmailValidationMixin
from shop.models.customer import CustomerModel
from shop.signals import email_queued


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
        widget=widgets.CheckboxInput(attrs={'class': 'form-check-input'}),
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
        subject_template = select_template([
            '{}/email/register-user-subject.txt'.format(app_settings.APP_LABEL),
            'shop/email/register-user-subject.txt',
        ])
        # Email subject *must not* contain newlines
        subject = ''.join(subject_template.render(context).splitlines())
        body_text_template = select_template([
            '{}/email/register-user-body.txt'.format(app_settings.APP_LABEL),
            'shop/email/register-user-body.txt',
        ])
        body_html_template = select_template([
            '{}/email/register-user-body.html'.format(app_settings.APP_LABEL),
            'shop/email/register-user-body.html',
        ], using='post_office')
        message = body_text_template.render(context)
        html_message = body_html_template.render(context)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        user.email_user(subject, message, from_email=from_email, html_message=html_message)
        email_queued()


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


class PasswordResetRequestForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        try:
            email_template = EmailTemplate.objects.get(name='password-reset-inform')
        except EmailTemplate.DoesNotExist:
            subject = render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            body = render_to_string(email_template_name, context)

            email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
            if html_email_template_name:
                template = get_template(html_email_template_name, using='post_office')
                html = template.render(context)
                email_message.attach_alternative(html, 'text/html')
                template.attach_related(email_message)
            email_message.send()
        else:
            context['user'] = str(context['user'])
            context['uid'] = context['uid'].decode('utf-8')
            post_office_mail.send(to_email, template=email_template, context=context, render_on_delivery=True)
        email_queued()
