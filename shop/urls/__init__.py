# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from . import rest_api
from . import payment


urlpatterns = (
    url(r'^api/', include(rest_api)),
    url(r'^payment/', include(payment)),
)
