# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms import widgets
from django.template import Context
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from djangular.forms import NgModelFormMixin, NgFormValidationMixin
from shop import settings as shop_settings
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3ModelForm


class RegisterUserForm(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    form_name = 'register_user_form'
    scope_prefix = 'form_data'
    field_css_classes = 'input-group has-feedback'

    email = fields.EmailField(label=_("Your e-mail address"))
    preset_password = fields.BooleanField(required=False, initial=True, label=_("Preset password"),
        widget=widgets.CheckboxInput(),
        help_text=_("Send a randomly generated password to your e-mail address."))

    password1 = fields.CharField(label=_("Choose a password"), widget=widgets.PasswordInput,
                                 min_length=6, help_text=_("Minimum length is 6 characters."))
    password2 = fields.CharField(label=_("Repeat password"), widget=widgets.PasswordInput,
                                 min_length=6, help_text=_("Must match other password."))

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2',)

    def __init__(self, data=None, instance=None, *args, **kwargs):
        if data and data.get('preset_password', False):
            password = self._meta.model.objects.make_random_password(8)
            data['password1'] = data['password2'] = password
        super(RegisterUserForm, self).__init__(data=data, instance=instance, *args, **kwargs)

    def as_div(self):
        # Intentionally rendered without fields `email` and `preset_password`
        self.fields.pop('email', None)
        self.fields.pop('preset_password', None)
        return super(RegisterUserForm, self).as_div()

    def clean(self):
        cleaned_data = super(RegisterUserForm, self).clean()
        if cleaned_data['password1'] != cleaned_data['password2']:
            msg = _("Passwords do not match")
            raise ValidationError(msg)
        if self._meta.model.objects.filter(username=cleaned_data['email']).exists():
            msg = _("A customer with the e-mail address '{email}' already exists.\n"
                    "If you have used this address previously, try to reset the password.")
            raise ValidationError(msg.format(**cleaned_data))
        return cleaned_data

    def save(self, request=None, commit=True):
        self.instance.is_registered = self.instance.is_active = True
        self.instance.username = self.cleaned_data['email']
        if self.cleaned_data['preset_password']:
            self._send_password(request)
        return super(RegisterUserForm, self).save(commit)

    def _send_password(self, request):
        from django.core.mail import send_mail
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = Context({
            'email': self.cleaned_data['email'],
            'password': self.cleaned_data['password1'],
            'domain': domain,
            'site_name': site_name,
            'user': request.user,
            'protocol': 'https' if request.is_secure() else 'http',
        })
        subject = select_template([
            '{}/email/register-user-subject.txt'.format(shop_settings.APP_LABEL),
            'shop/email/register-user-subject.txt',
        ]).render(context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = select_template([
            '{}/email/register-user-body.txt'.format(shop_settings.APP_LABEL),
            'shop/email/register-user-body.txt',
        ]).render(context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [context['email']])
