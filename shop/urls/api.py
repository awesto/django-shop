# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets, views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.response import Response
from shop.views.cart import CartViewSet


# TODO: remove this later
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ModelViewSet):
    # TODO: remove this later
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return self.queryset


router = routers.DefaultRouter()  # trailing_slash=False
router.register(r'users', UserViewSet)  # TODO: remove this later
router.register(r'cart', CartViewSet, base_name='cart')

urlpatterns = (
    url(r'^', include(router.urls)),
)
