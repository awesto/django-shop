from django.conf import settings
from django.template.loader import select_template
from django.urls import NoReverseMatch, reverse
from django.utils.translation import get_language_from_request
from cms.models.pagemodel import Page
from rest_framework.serializers import CharField, BooleanField
from rest_auth import serializers
from shop.conf import app_settings
from shop.forms.auth import PasswordResetRequestForm
from rest_auth.serializers import LoginSerializer as DefaultLoginSerializer


class LoginSerializer(DefaultLoginSerializer):
    stay_logged_in = BooleanField(required=False)


class PasswordResetRequestSerializer(serializers.PasswordResetSerializer):
    template_prefix = 'password-reset'
    password_reset_form_class = PasswordResetRequestForm
    invalid_password_reset_confirm_url = '/cms-page_or_view_with__reverse_id=password-reset-confirm__does-not-exist/'

    def save(self):
        subject_template = select_template([
            '{}/email/{}-subject.txt'.format(app_settings.APP_LABEL, self.template_prefix),
            'shop/email/{}-subject.txt'.format(self.template_prefix),
        ])
        body_text_template = select_template([
            '{}/email/{}-body.txt'.format(app_settings.APP_LABEL, self.template_prefix),
            'shop/email/{}-body.txt'.format(self.template_prefix),
        ])
        body_html_template = select_template([
            '{}/email/{}-body.html'.format(app_settings.APP_LABEL, self.template_prefix),
            'shop/email/{}-body.html'.format(self.template_prefix),
        ])
        try:
            page = Page.objects.select_related('node').get(reverse_id='password-reset-confirm', publisher_is_draft=False)
        except Page.DoesNotExist:
            try:
                password_reset_confirm_url = reverse('password-reset-confirm')
            except NoReverseMatch:
                password_reset_confirm_url = self.invalid_password_reset_confirm_url
        else:
            language = get_language_from_request(self.context['request'])
            password_reset_confirm_url = page.get_absolute_url(language)
        opts = {
            'use_https': self.context['request'].is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': self.context['request'],
            'subject_template_name': subject_template.template.name,
            'email_template_name': body_text_template.template.name,
            'html_email_template_name': body_html_template.template.name,
            'extra_email_context': {'password_reset_confirm_url': password_reset_confirm_url}
        }
        self.reset_form.save(**opts)


class RegisterUserActivateSerializer(PasswordResetRequestSerializer):
    template_prefix = 'register-user-activate'


class PasswordResetConfirmSerializer(serializers.PasswordResetConfirmSerializer):
    new_password1 = CharField(min_length=6, max_length=128)
    new_password2 = CharField(min_length=6, max_length=128)
