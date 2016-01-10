# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from shop.views import ShopTemplateView


urlpatterns = [
    url(r'^$', ShopTemplateView.as_view(template_name="shop/welcome.html"),
        name='shop_welcome'),
    (r'^pay/', include('shop.urls.payment')),
    (r'^ship/', include('shop.urls.shipping')),
    (r'^orders/', include('shop.urls.order')),
    (r'^checkout/', include('shop.urls.checkout')),
    (r'^cart/', include('shop.urls.cart')),
    (r'^products/', include('shop.urls.catalog')),
]
