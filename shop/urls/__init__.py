# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from shop.views import ShopTemplateView


urlpatterns = patterns('',
    url(r'^$', ShopTemplateView.as_view(template_name="shop/welcome.html"),
        name='shop_welcome'),
    (r'^pay/', include('shop.payment.urls')),
    (r'^ship/', include('shop.shipping.urls')),
    (r'^orders/', include('shop.urls.order')),
    (r'^checkout/', include('shop.urls.checkout')),
    (r'^cart/', include('shop.urls.cart')),
    (r'^products/', include('shop.urls.catalog')),
    )
