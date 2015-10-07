# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.db.models import Q
from rest_framework.settings import api_settings
from shop.rest.filters import CMSPagesFilterBackend
from shop.views.product import AddToCartView, ProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.models.commodity import Commodity
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
    AddToCartSerializer, CommoditySearchSerializer)

limit_choices_to = Q(instance_of=Commodity, active=True)
list_options = dict(
    product_model=Commodity,
    serializer_class=ProductSummarySerializer,
    filter_backends=api_settings.DEFAULT_FILTER_BACKENDS + [CMSPagesFilterBackend],
    limit_choices_to=limit_choices_to,
)
detail_options = dict(
    serializer_class=ProductDetailSerializer,
    lookup_field='translations__slug',
    limit_choices_to=limit_choices_to,
)
add2cart_options = dict(
    serializer_class=AddToCartSerializer,
    lookup_field='translations__slug',
    limit_choices_to=limit_choices_to,
)
autocomplete_options = dict(
    serializer_class=CommoditySearchSerializer,
    index_models=[Commodity],
)


urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(**list_options)),
    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(**detail_options)),
    url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(**add2cart_options)),
    url(r'^autocomplete/', SearchView.as_view(**autocomplete_options)),
)
