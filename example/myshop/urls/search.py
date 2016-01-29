# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from shop.search.views import SearchView
from myshop.serializers import ProductSearchSerializer

urlpatterns = patterns('',
    url(r'^', SearchView.as_view(
        serializer_class=ProductSearchSerializer,
    )),
)
