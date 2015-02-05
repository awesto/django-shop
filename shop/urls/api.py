# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets, views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.response import Response

from shop.models.cart import BaseCart, BaseCartItem
from shop.views.cart import CartViewSet


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# class UserDetailView(views.APIView):
#     serializer_class = UserSerializer
#
#     def get(self, request, format=None):
#         user = User.objects.get(pk=2)
#         serializer = UserSerializer(user, context={'request': request})
#         return Response(serializer.data)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return self.queryset



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'cart', CartViewSet, base_name='cart')


urlpatterns = (
    url(r'^', include(router.urls)),
)

# urlpatterns = format_suffix_patterns((
#     url(r'^product-list/$', product_list),
#     url(r'^product-detail/(?P<pk>[0-9]+)$', product_detail),
#     url(r'^cart/(?P<pk>[0-9]+)$', CartItemView.as_view()),
#     #url(r'^', include(router.urls)),
# ))
