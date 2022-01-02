from django.conf.urls import include, url
from shop.shopurls import rest_api
from shop.shopurls import auth
from shop.shopurls import payment


app_name = 'shop'

urlpatterns = [
    url(r'^api/', include(rest_api)),
    url(r'^auth/', include(auth)),
    url(r'^payment/', include(payment)),
]
