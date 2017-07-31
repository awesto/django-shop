# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

from . import rest_api
from . import auth
from . import payment


urlpatterns = [
    url(r'^api/', include(rest_api)),
    url(r'^auth/', include(auth)),
    url(r'^payment/', include(payment)),
]
