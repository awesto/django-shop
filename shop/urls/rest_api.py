# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url, include
from rest_framework import routers
from shop.views.cart import CartViewSet, WatchViewSet
from shop.views.checkout import CheckoutViewSet
from shop.views.catalog import ProductSelectView

router = routers.DefaultRouter()  # TODO: try with trailing_slash=False
router.register(r'cart', CartViewSet, base_name='cart')
router.register(r'watch', WatchViewSet, base_name='watch')
router.register(r'checkout', CheckoutViewSet, base_name='checkout')

urlpatterns = [
    url(r'^select_product/?$', ProductSelectView.as_view(), name='select-product'),
    url(r'^', include(router.urls)),
]
