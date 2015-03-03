# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from shop.views.cart import CartViewSet, WatchViewSet
from rest_framework import routers

router = routers.DefaultRouter()  # trailing_slash=False
router.register(r'cart', CartViewSet, base_name='cart')
router.register(r'watch', WatchViewSet, base_name='watch')

urlpatterns = (
    url(r'^', include(router.urls)),
)
