# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from shop.views.order import OrderView

urlpatterns = [
    url(r'^$', OrderView.as_view()),
    url(r'^(?P<slug>[\w-]+)/?$', OrderView.as_view(many=False)),
]
