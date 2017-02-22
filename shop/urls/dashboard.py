# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include

from shop.views.dashboard import router


urlpatterns = [
    url(r'^', include(router.urls)),
]
