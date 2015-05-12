# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template.loader import select_template
from rest_auth import serializers
from shop import settings as shop_settings


class PasswordResetSerializer(serializers.PasswordResetSerializer):
    def save(self):
        subject_template = select_template([
            '{}/email/reset-password-subject.txt'.format(shop_settings.APP_LABEL),
            'shop/email/reset-password-subject.txt',
        ])
        body_template = select_template([
            '{}/email/reset-password-body.txt'.format(shop_settings.APP_LABEL),
            'shop/email/reset-password-body.txt',
        ])
        opts = {
            'use_https': self.context['request'].is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': self.context['request'],
            'subject_template_name': subject_template.name,
            'email_template_name': body_template.name,
        }
        self.reset_form.save(**opts)
