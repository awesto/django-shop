# -*- coding: utf-8 -*-
"""
These URL routings are used by the example `i18n_commodity` as found in the djangoSHOP's tutorials.
The difference here is that we modified the lookup_field for slug, since it is translated.
"""
from __future__ import unicode_literals

from django.conf.urls import url
from shop.views.catalog import AddToCartView, CMSPageProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
                                CatalogSearchSerializer)

urlpatterns = [
    url(r'^$', CMSPageProductListView.as_view(
        serializer_class=ProductSummarySerializer,
    )),
    url(r'^search-catalog$', SearchView.as_view(
        serializer_class=CatalogSearchSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer,
        lookup_field='translations__slug'
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
        lookup_field = 'translations__slug'
    )),
]
