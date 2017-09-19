# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import select_template

from rest_framework.serializers import CharField
from rest_auth import serializers

from shop.conf import app_settings


class PasswordResetSerializer(serializers.PasswordResetSerializer):
    base_template = 'reset-password'

    def save(self):
        subject_template = select_template([
            '{}/email/{}-subject.txt'.format(app_settings.APP_LABEL, self.base_template),
            'shop/email/{}-subject.txt'.format(self.base_template),
        ])
        body_template = select_template([
            '{}/email/{}-body.txt'.format(app_settings.APP_LABEL, self.base_template),
            'shop/email/{}-body.txt'.format(self.base_template),
        ])
        opts = {
            'use_https': self.context['request'].is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': self.context['request'],
            'subject_template_name': subject_template.template.name,
            'email_template_name': body_template.template.name,
        }
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.PasswordResetConfirmSerializer):
    new_password1 = CharField(min_length=6, max_length=128)
    new_password2 = CharField(min_length=6, max_length=128)
