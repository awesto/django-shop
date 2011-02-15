#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from shop.models.productmodel import Product, Category
from shop.views import ShopListView, ShopTemplateView
from shop.views.cart import CartDetails
from shop.views.category import CategoryDetailView
from shop.views.checkout import SelectShippingView, SelectPaymentView
from shop.views.product import ProductDetailView

# Loop through payment backends and mount the modules in pay/
urlpatterns = patterns('',
    (r'^pay/', include('shop.payment.urls')),
    (r'^ship/', include('shop.shipping.urls')),
    
    #Home
    url(r'^$', ShopTemplateView.as_view(template_name="shop/welcome.html")),
    
    # Cart
    url(r'^cart/$', CartDetails.as_view(), 
        name='cart'
        ),
    
    # Checkout
    url(r'^checkout/ship/$', SelectShippingView.as_view(), 
        name='checkout_shipping' # First step of the checkout process
        ),
    url(r'^checkout/pay/$', SelectPaymentView.as_view(), 
        name='checkout_payment' # Second step of the checkout process
        ),
    
    # Products
    url(r'^products/$',
        ShopListView.as_view(model=Product),
        name='product_list'
        ),
    url(r'^products/(?P<slug>[0-9A-Za-z-_.//]+)/$',
        ProductDetailView.as_view(),
        name='product_detail'
        ),
        
    # Categories
    url(r'^categories/$',
        ShopListView.as_view(model=Category),
        name='category_list'
        ),
    url(r'^categories/(?P<slug>[0-9A-Za-z-_.//]+)/$',
        CategoryDetailView.as_view(),
        name='category_detail'
        ),
)
