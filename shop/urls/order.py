# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from shop.views.order import OrderListView, OrderRetrieveView

urlpatterns = patterns('',
    url(r'^$', OrderListView.as_view(), name='order-list'),
    url(r'^(?P<pk>\d+)$', OrderRetrieveView.as_view(), name='order-detail'),
    url(r'^last$', OrderRetrieveView.as_view(fetch_last=True), name='order-detail-last'),
)
