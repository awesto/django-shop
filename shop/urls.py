#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from shop.models.productmodel import Product, Category
from shop.views import ShopDetailView, ShopListView, ShopTemplateView
from shop.views.cart import CartDetails
from shop.views.category import CategoryDetailView
from shop.views.checkout import SelectShippingView

# Loop through payment backends and mount the modules in pay/
urlpatterns = patterns('',
    (r'^pay/$', include('shop.payment.urls')),
    (r'^ship/$', include('shop.shipping.urls')),
    
    #Home
    url(r'^$', ShopTemplateView.as_view(template_name="shop/welcome.html")),
    
    # Cart
    url(r'^cart/$', CartDetails.as_view(), 
        name='cart' # NOT cart_detail since we can POST to it to add stuff
        ),
    
    # Checkout
    url(r'^checkout/$', SelectShippingView.as_view(), 
        name='checkout' # NOT cart_detail since we can POST to it to add stuff
        ),
    
    # Products
    url(r'^product/(?P<slug>[0-9A-Za-z-_.//]+)/$',
        ShopDetailView.as_view(model=Product),
        name='product_detail'
        ),
    url(r'^products/$',
        ShopListView.as_view(model=Product),
        name='product_list'
        ),
        
    # Categories
    url(r'^categories/$',
        ShopListView.as_view(model=Category),
        name='category_list'
        ),
    url(r'^category/(?P<slug>[0-9A-Za-z-_.//]+)/$',
        CategoryDetailView.as_view(),
        name='category_detail'
        ),
)
