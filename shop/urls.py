#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include

# Loop through payment backends and mount the modules in pay/
urlpatterns = patterns('',
    (r'^pay/$', include('shop.payment.urls')),
)
