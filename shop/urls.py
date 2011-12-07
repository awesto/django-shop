#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include

from shop import (
        urls_catalog,
        urls_cart,
        urls_checkout,
        urls_order,
        )


urlpatterns = patterns('',
    (r'^pay/', include('shop.payment.urls')),
    (r'^ship/', include('shop.shipping.urls')),
    (r'', include(urls_order)),
    (r'', include(urls_checkout)),
    (r'', include(urls_cart)),
    (r'', include(urls_catalog)),
    )
