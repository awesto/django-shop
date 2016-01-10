from django.conf.urls import url
from shop.views.order import OrderListView, OrderDetailView

urlpatterns = [
    url(r'^$',
        OrderListView.as_view(),
        name='order_list'),
    url(r'^(?P<pk>\d+)/$',
        OrderDetailView.as_view(),
        name='order_detail'),
]

