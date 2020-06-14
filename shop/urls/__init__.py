from django.conf.urls import include, url
from shop.urls import rest_api
from shop.urls import auth
from shop.urls import payment


app_name = 'shop'

urlpatterns = [
    url(r'^api/', include(rest_api)),
    url(r'^auth/', include(auth)),
    url(r'^payment/', include(payment)),
]
