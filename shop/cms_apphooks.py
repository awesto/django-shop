# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp


class CatalogListCMSApp(CMSApp):
    name = _("Catalog List")

    def get_urls(self, page=None, language=None, **kwargs):
        raise ImproperlyConfigured("`CatalogListApp must implement method `get_urls`.")


class CatalogSearchCMSApp(CMSApp):
    name = _("Catalog Search")

    def get_urls(self, page=None, language=None, **kwargs):
        raise ImproperlyConfigured("`CatalogSearchCMSApp` must implement method `get_urls`.")


class OrderCMSApp(CMSApp):
    name = _("View Orders")
    cache_placeholders = False

    def get_urls(self, page=None, language=None, **kwargs):
        from django.conf.urls import url
        from shop.views.order import OrderView

        if page and page.reverse_id == 'shop-order-last':
            return [
                url(r'^$', OrderView.as_view(many=False, is_last=True)),
            ]
        return [
            url(r'^$', OrderView.as_view()),
            url(r'^(?P<slug>[\w-]+)/?$', OrderView.as_view(many=False)),
        ]
