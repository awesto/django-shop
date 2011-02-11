#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from shop.views.cart import CartDetails

# Loop through payment backends and mount the modules in pay/
urlpatterns = patterns('',
    (r'^pay/$', include('shop.payment.urls')),
    (r'^ship/$', include('shop.shipping.urls')),
    url(r'^cart/$', CartDetails.as_view()),
)
