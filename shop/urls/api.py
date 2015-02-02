# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns
from shop.serializers.product import product_list, product_detail
from shop.views.cart import CartView, CartItemView


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
#router = routers.DefaultRouter()
#router.register(r'users', UserViewSet)


urlpatterns = format_suffix_patterns((
    url(r'^product-list/$', product_list),
    url(r'^product-detail/(?P<pk>[0-9]+)$', product_detail),
    url(r'^cart/$', CartView.as_view()),
    url(r'^cart/(?P<pk>[0-9]+)$', CartItemView.as_view()),
    #url(r'^', include(router.urls)),
))
