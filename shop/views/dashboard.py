# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import BrowsableAPIRenderer
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
            product = self.get_object()
            return self.list_serializer_class  # TODO: use the correct
        msg = "ViewSet 'ProductsDashboard' is not implemented for action '{}'"
        raise NotImplementedError(msg.format(self.action))

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        #context.update(many=kwargs.get('many', False))
        kwargs.update(context=context, label='dashboard')
        list_fields = ['pk']
        list_fields.extend(self.get_list_display())
        serializer_class.Meta.fields = list_fields  # reorder the fields
        return serializer_class(*args, **kwargs)

    def get_list_display(self):
        if hasattr(self, 'list_display'):
            return self.list_display
        return self.list_serializer_class.Meta.fields

    def get_list_display_links(self):
        if hasattr(self, 'list_display_links'):
            return self.list_display_links
        return self.get_list_display()[:1]

    def get_template_names(self):
        # TODO: this could be moved to the DashboardRenderer
        app_label = app_settings.APP_LABEL
        if self.action == 'list':
            return [
                os.path.join(app_label, 'dashboard/product-list.html'),
                'shop/dashboard/product-list.html',
            ]
        elif self.action == 'retrieve':
            product = self.get_object()
            return [
                os.path.join(app_label, 'dashboard/{}-detail.html'.format(product.product_model)),
                os.path.join(app_label, 'dashboard/product-detail.html'),
                'shop/dashboard/product-detail.html',
            ]
