# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from rest_framework.settings import api_settings
from shop.rest.filters import CMSPagesFilterBackend
from shop.views.catalog import AddToCartView, ProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
    AddSmartphoneToCartSerializer)
from myshop.models.polymorphic.smartphone import SmartPhone

urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(
        serializer_class=ProductSummarySerializer,
        filter_backends=api_settings.DEFAULT_FILTER_BACKENDS + [CMSPagesFilterBackend()],
    )),
    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
    url(r'^smartphone/(?P<product_code>\d+)/add-to-cart', AddToCartView.as_view(
        product_model=SmartPhone,
        serializer_class=AddSmartphoneToCartSerializer,
        lookup_field='product_code',
        lookup_url_kwarg='product_code',
    ), name='add-smartphone-to-cart'),
    url(r'^autocomplete/', SearchView.as_view()),
)
