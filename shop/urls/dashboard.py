# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include

from shop.views.dashboard import router, DashboardView


urlpatterns = [
    url(r'^$', DashboardView.as_view(), name='root'),
    url(r'^', include(router.urls)),
]
