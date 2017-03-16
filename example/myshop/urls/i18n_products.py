# -*- coding: utf-8 -*-
"""
These URL routings are used by the example `i18n_commodity` as found in the django-SHOP's tutorials.
The difference here is that we modified the lookup_field for slug, since it is translated.
"""
from __future__ import unicode_literals

from django.conf.urls import url

from shop.views.catalog import ProductListView, ProductRetrieveView, AddToCartView

from myshop.serializers import ProductSummarySerializer, ProductDetailSerializer

urlpatterns = [
    url(r'^$', ProductListView.as_view(
        serializer_class=ProductSummarySerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer,
        lookup_field='translations__slug'
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
        lookup_field='translations__slug'
    )),
]
