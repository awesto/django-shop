# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from rest_framework.settings import api_settings
from shop.rest.filters import CMSPagesFilterBackend
from shop.views.product import AddToCartView, ProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
    AddToCartSerializer)

list_options = dict(
    serializer_class=ProductSummarySerializer,
    filter_backends=api_settings.DEFAULT_FILTER_BACKENDS + [CMSPagesFilterBackend()],
)
detail_options = dict(
    serializer_class=ProductDetailSerializer,
    lookup_field='slug',
)
smartphone2cart_options = dict(
    serializer_class=AddToCartSerializer,
    lookup_field='product_code',
    lookup_url_kwarg='product_code',
)

urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(**list_options)),
    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(**detail_options)),
    url(r'^smartphone/(?P<product_code>\d+)/add-to-cart',
        AddToCartView.as_view(**smartphone2cart_options), name='add-smartphone-to-cart'),
    url(r'^autocomplete/', SearchView.as_view()),
)
