# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from shop.search.views import SearchView
from myshop.models.commodity import Commodity
from myshop.serializers import ProductSearchSerializer


autocomplete_options = dict(
    serializer_class=ProductSearchSerializer,
    index_models=[Commodity],
)
urlpatterns = patterns('',
    url(r'^', SearchView.as_view(**autocomplete_options)),
)
