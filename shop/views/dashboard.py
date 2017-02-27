# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import routers

from shop import app_settings
from shop.models.product import ProductModel
from shop.rest.money import JSONRenderer
from shop.rest.renderers import DashboardRenderer

router = routers.DefaultRouter()


class DashboardPaginator(LimitOffsetPagination):
    default_limit = 20


class ProductsDashboard(viewsets.ModelViewSet):
    renderer_classes = (DashboardRenderer, JSONRenderer, BrowsableAPIRenderer)
    pagination_class = DashboardPaginator
    list_serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
    detail_serializer_classes = {}
    queryset = ProductModel.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        elif self.action == 'retrieve':
            #return self.list_serializer_class
            instance = self.get_object()
            return self.detail_serializer_classes.get(instance._meta.label_lower,
                                                      self.list_serializer_class)
        msg = "ViewSet 'ProductsDashboard' is not implemented for action '{}'"
        return self.list_serializer_class  # TODO: use the correct
        raise NotImplementedError(msg.format(self.action))

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        kwargs.update(context=context, label='dashboard')
        if kwargs.get('many', False):
            list_fields = ['pk']
            list_fields.extend(self.get_list_display())
            serializer_class.Meta.fields = list_fields  # reorder the fields
        serializer = serializer_class(*args, **kwargs)
        return serializer

    def get_list_display(self):
        if hasattr(self, 'list_display'):
            return self.list_display
        return self.list_serializer_class.Meta.fields

    def get_list_display_links(self):
        if hasattr(self, 'list_display_links'):
            return self.list_display_links
        return self.get_list_display()[:1]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'serializer': serializer, 'instance': instance})
