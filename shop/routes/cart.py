# -*- coding: utf-8 -*-
from shop.views.cart import CartViewSet, WatchViewSet
from . import shop_router

shop_router.register(r'cart', CartViewSet, base_name='cart')
shop_router.register(r'watch', WatchViewSet, base_name='watch')
