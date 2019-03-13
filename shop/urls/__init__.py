# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from shop.urls import rest_api
from shop.urls import auth
from shop.urls import payment


urlpatterns = [
    url(r'^api/', include(rest_api)),
    url(r'^auth/', include(auth)),
    url(r'^payment/', include(payment)),
]
