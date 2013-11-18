from django.conf.urls import patterns, url
from shop.views.product import (ProductListView, ProductDetailView)


urlpatterns = patterns('',
    url(r'^$',
        ProductListView.as_view(),
        name='product_list'
        ),
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$',
        ProductDetailView.as_view(),
        name='product_detail'
        ),
    )
