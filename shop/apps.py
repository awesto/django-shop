# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = _("Shop")

    def ready(self):
        from django_fsm.signals import post_transition
        from jsonfield.fields import JSONField
        from rest_framework.serializers import ModelSerializer
        from shop.models.notification import order_event_notification
        from shop.rest.serializers import JSONSerializerField

        post_transition.connect(order_event_notification)

        # add JSONField to the map of customized serializers
        ModelSerializer.serializer_field_mapping[JSONField] = JSONSerializerField
