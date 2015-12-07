# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from rest_framework.settings import api_settings
from shop.rest.filters import CMSPagesFilterBackend
from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
    AddSmartphoneToCartSerializer)

urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(
        serializer_class=ProductSummarySerializer,
        filter_backends=api_settings.DEFAULT_FILTER_BACKENDS + [CMSPagesFilterBackend()],
    )),
    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
    url(r'^(?P<slug>[\w-]+)/add-smartphone-to-cart', AddToCartView.as_view(
        serializer_class=AddSmartphoneToCartSerializer,
    )),
    url(r'^autocomplete/', SearchView.as_view()),
)
