# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = _("Shop")

    def ready(self):
        from django_fsm.signals import post_transition
        from shop.models.fields import JSONField
        from rest_framework.serializers import ModelSerializer
        from shop.deferred import ForeignKeyBuilder
        from shop.rest.fields import JSONSerializerField
        from shop.models.notification import order_event_notification

        post_transition.connect(order_event_notification)

        # add JSONField to the map of customized serializers
        ModelSerializer.serializer_field_mapping[JSONField] = JSONSerializerField

        # perform some sanity checks
        ForeignKeyBuilder.check_for_pending_mappings()

        # add pending patches to Django-CMS
        self.monkeypatch_django_cms()

    def monkeypatch_django_cms(self):
        """
        This monkey patch can be removed when https://github.com/divio/django-cms/pull/5898
        has been merged
        """
        from importlib import import_module
        from django.core.exceptions import ImproperlyConfigured
        from django.utils import six
        from cms import appresolver

        def get_app_urls(urls):
            for urlconf in urls:
                if isinstance(urlconf, six.string_types):
                    mod = import_module(urlconf)
                    if not hasattr(mod, 'urlpatterns'):
                        raise ImproperlyConfigured(
                            "URLConf `%s` has no urlpatterns attribute" % urlconf)
                    yield getattr(mod, 'urlpatterns')
                else:
                    yield [urlconf]

        appresolver.get_app_urls = get_app_urls
