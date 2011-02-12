#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from shop.models.productmodel import Product
from shop.views import ShopDetailView, ShopListView
from shop.views.cart import CartDetails

# Loop through payment backends and mount the modules in pay/
urlpatterns = patterns('',
    (r'^pay/$', include('shop.payment.urls')),
    (r'^ship/$', include('shop.shipping.urls')),
    
    url(r'^cart/$', CartDetails.as_view()),
    
    url(r'^product/(?P<slug>[0-9A-Za-z-_.//]+)/$',
        ShopDetailView.as_view(model=Product, 
                               template_name="shop/product/product_detail.html"),
        name='product_detail'
        ),
    url(r'^products/$',
        ShopListView.as_view(model=Product, template_name="shop/product/product_list.html"),
        name='product_list'
        ),
)
