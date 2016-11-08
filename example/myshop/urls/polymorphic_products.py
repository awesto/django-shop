# -*- coding: utf-8 -*-
"""
These URL routings are used by the example `polymorphic` as found in the django-SHOP's tutorials.
The difference here is that we added a special serializer class to add smart phones with their
variations to the cart.
"""
from __future__ import unicode_literals

from django.conf.urls import url
from shop.views.catalog import AddToCartView, CMSPageProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.filters import ManufacturerFilter
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
                                AddSmartCardToCartSerializer, AddSmartPhoneToCartSerializer,
                                CatalogSearchSerializer)

urlpatterns = [
    url(r'^$', CMSPageProductListView.as_view(
        serializer_class=ProductSummarySerializer,
        filter_class=ManufacturerFilter,
    )),
    url(r'^search-catalog$', SearchView.as_view(
        serializer_class=CatalogSearchSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/?$', ProductRetrieveView.as_view(
        serializer_class=ProductDetailSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
        serializer_class=AddSmartCardToCartSerializer,
    )),
    url(r'^(?P<slug>[\w-]+)/add-smartphone-to-cart', AddToCartView.as_view(
        serializer_class=AddSmartPhoneToCartSerializer,
    )),
]
