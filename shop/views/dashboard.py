# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework import viewsets
from rest_framework import routers

from shop import app_settings
from shop.models.product import ProductModel
from shop.rest.money import JSONRenderer

router = routers.DefaultRouter()


class DashboardPaginator(LimitOffsetPagination):
    default_limit = 20


class ProductsDashboard(viewsets.ModelViewSet):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    pagination_class = DashboardPaginator
    list_serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
    detail_serializer_classes = {}
    queryset = ProductModel.objects.all()
    list_display = ['product_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return app_settings.PRODUCT_SUMMARY_SERIALIZER
        elif self.action == 'retrieve':
            product = self.get_object()
            return app_settings.PRODUCT_SUMMARY_SERIALIZER
        msg = "ViewSet 'ProductsDashboard' is not implemented for action '{}'"
        raise NotImplementedError(msg.format(self.action))

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        context.update(many=kwargs.get('many', False))
        kwargs.update(
            context=self.get_serializer_context(),
            label='dashboard',
        )
        return serializer_class(*args, **kwargs)

    def get_renderer_context(self):
        context = super(ProductsDashboard, self).get_renderer_context()
        return context

    def get_template_names(self):
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
