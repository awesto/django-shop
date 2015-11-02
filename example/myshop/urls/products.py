# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.db.models import Q
from rest_framework.settings import api_settings
from shop.rest.filters import CMSPagesFilterBackend
from shop.views.product import AddToCartView, ProductListView, ProductRetrieveView
from shop.search.views import SearchView
from myshop.models.smartphone import SmartPhoneModel, SmartPhone
from myshop.serializers import (ProductSummarySerializer, ProductDetailSerializer,
    AddToCartSerializer, CommoditySearchSerializer)

limit_choices_to = Q(instance_of=SmartPhoneModel, active=True)
list_options = dict(
    product_model=SmartPhoneModel,
    serializer_class=ProductSummarySerializer,
    filter_backends=api_settings.DEFAULT_FILTER_BACKENDS + [CMSPagesFilterBackend()],
    limit_choices_to=limit_choices_to,
)
detail_options = dict(
    serializer_class=ProductDetailSerializer,
    lookup_field='slug',
    limit_choices_to=limit_choices_to,
)
smartphone2cart_options = dict(
    serializer_class=AddToCartSerializer,
    lookup_field='product_code',
    lookup_url_kwarg='product_code',
    product_model=SmartPhone,
)


urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(**list_options)),
    url(r'^(?P<slug>[\w-]+)$', ProductRetrieveView.as_view(**detail_options)),
    url(r'^smartphone/(?P<product_code>\d+)/add-to-cart',
        AddToCartView.as_view(**smartphone2cart_options), name='add-smartphone-to-cart'),
    url(r'^autocomplete/', SearchView.as_view()),
)
