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
        from jsonfield.fields import JSONField
        from rest_framework.serializers import ModelSerializer
        from shop.rest.serializers import JSONSerializerField
        from shop.models.notification import order_event_notification

        post_transition.connect(order_event_notification)

        # Monkey patches for Django-1.8
        if get_tuple_version()[:2] < (1, 9):
            from django.utils import numberformat
            from shop.patches import numberformat as patched_numberformat
            numberformat.format = patched_numberformat.format

        # add JSONField to the map of customized serializers
        ModelSerializer.serializer_field_mapping[JSONField] = JSONSerializerField


def get_tuple_version(version=None):
    version = version or get_version()
    return tuple(map(lambda n: int(n), version.split('.')))
