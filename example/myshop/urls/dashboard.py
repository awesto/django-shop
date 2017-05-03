# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include

from shop.dashboard.routers import DashboardRouter
from shop.dashboard.views import FileUploadView

from myshop.dashboard import ProductsDashboard

router = DashboardRouter(trailing_slash=False)
router.register('products', ProductsDashboard)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^upload/$', FileUploadView.as_view(), name='fileupload')
]
