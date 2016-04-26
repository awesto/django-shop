# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from shop.views.order import OrderView
from myshop.serializers import OrderDetailSerializer

urlpatterns = patterns('',
    url(r'^$', OrderView.as_view()),
    url(r'^(?P<pk>\d+)$', OrderView.as_view(many=False,
        detail_serializer_class=OrderDetailSerializer)),
)
