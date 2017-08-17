# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from cms.apphook_pool import apphook_pool

from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView
from shop.cms_apphooks import CatalogListCMSApp, OrderCMSApp

from .serializers import ProductSummarySerializer, ProductDetailSerializer


class CatalogListApp(CatalogListCMSApp):
    def get_urls(self, page=None, language=None, **kwargs):
        return [
            url(r'^$', ProductListView.as_view(
                serializer_class=ProductSummarySerializer,
            )),
            url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(
                serializer_class=ProductDetailSerializer
            )),
            url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
        ]

apphook_pool.register(CatalogListApp)
