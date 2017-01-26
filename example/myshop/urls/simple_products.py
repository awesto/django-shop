# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
These URL routings are used by the example `commodity`, `smartcard` and `i18n_smartcard` as found
in the django-SHOP's tutorials.
This is the simplest way of routing and a good default to start with.
"""

from django.conf.urls import url

from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView

from myshop.serializers import ProductSummarySerializer, ProductDetailSerializer

urlpatterns = [
    url(r'^$', ProductListView.as_view(
        serializer_class=ProductSummarySerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
]
