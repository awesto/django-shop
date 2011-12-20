from django.conf.urls.defaults import patterns, url

from shop.views.order import OrderListView, OrderDetailView

urlpatterns = patterns('',
    url(r'^$',
        OrderListView.as_view(),
        name='order_list'),
    url(r'^(?P<pk>\d+)/$',
        OrderDetailView.as_view(),
        name='order_detail'),
    )

