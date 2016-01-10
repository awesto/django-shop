from django.conf.urls import url
from shop.views.product import (ProductListView, ProductDetailView)


urlpatterns = [
    url(r'^$',
        ProductListView.as_view(),
        name='product_list'
        ),
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$',
        ProductDetailView.as_view(),
        name='product_detail'
        ),
]
