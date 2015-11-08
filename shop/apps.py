# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import get_version
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = _("Shop")

    def ready(self):
        from django_fsm.signals import post_transition
        from shop.models.notification import order_event_notification

        post_transition.connect(order_event_notification)

        # Monkey patches for Django-1.7
        if get_version() < (1, 8):
            from django.utils import numberformat
            from shop.patches import numberformat as patched_numberformat
            numberformat.format = patched_numberformat.format
