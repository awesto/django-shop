# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from rest_framework.settings import api_settings
from shop.rest.filters import CMSPagesFilterBackend
from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
    CatalogSearchSerializer)

filter_backends = list(api_settings.DEFAULT_FILTER_BACKENDS)
filter_backends.append(CMSPagesFilterBackend())

urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(
        serializer_class=ProductSummarySerializer,
        filter_backends=filter_backends,
    )),
    url(r'^search-catalog$', SearchView.as_view(
        serializer_class=CatalogSearchSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
)
