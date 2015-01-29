# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^pay/', include('shop.payment.urls')),
    url(r'^ship/', include('shop.shipping.urls')),
    url(r'^orders/', include('shop.urls.order')),
    url(r'^checkout/', include('shop.urls.checkout')),
    url(r'^cart/', include('shop.urls.cart')),
    url(r'^products/', include('shop.urls.catalog')),
)
