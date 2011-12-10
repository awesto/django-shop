from django.conf.urls.defaults import patterns, url

from shop.views.order import OrderListView, OrderDetailView

urlpatterns = patterns('',
    url(r'^orders/$',
        OrderListView.as_view(),
        name='order_list'),
    url(r'^orders/(?P<pk>\d+)/$',
        OrderDetailView.as_view(),
        name='order_detail'),
    )

