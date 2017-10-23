# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.cache import never_cache

from rest_framework import generics, mixins
from rest_framework.exceptions import NotFound, PermissionDenied, MethodNotAllowed
from rest_framework.renderers import BrowsableAPIRenderer

from shop.rest.money import JSONRenderer
from shop.rest.renderers import CMSPageRenderer
from shop.serializers.order import OrderListSerializer, OrderDetailSerializer
from shop.models.order import OrderModel


class OrderView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                generics.GenericAPIView):
    """
    Base View class to render the fulfilled orders for the current user.
    """
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    list_serializer_class = OrderListSerializer
    detail_serializer_class = OrderDetailSerializer
    lookup_field = lookup_url_kwarg = 'slug'
    many = True
    is_last = False

    def get_queryset(self):
        return OrderModel.objects.filter_from_request(self.request)

    def get_serializer_class(self):
        if self.many:
            return self.list_serializer_class
        return self.detail_serializer_class

    def get_renderer_context(self):
        renderer_context = super(OrderView, self).get_renderer_context()
        if self.request.accepted_renderer.format == 'html':
            renderer_context.update(many=self.many, is_last=self.is_last)
            if self.many is False and self.is_last is False:
                # add an extra ance to the breadcrumb to show the order number
                try:
                    renderer_context['extra_ance'] = self.get_object().get_number()
                except (AttributeError, PermissionDenied):
                    pass
        return renderer_context

    def get_object(self):
        if self.lookup_url_kwarg not in self.kwargs:
            return self.get_queryset().first()
        return super(OrderView, self).get_object()

    @property
    def allowed_methods(self):
        """Restrict method "POST" only on the detail view"""
        allowed_methods = self._allowed_methods()
        if self.many:
            allowed_methods.remove('POST')
        return allowed_methods

    @never_cache
    def get(self, request, *args, **kwargs):
        if self.many:
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.many:
            raise MethodNotAllowed("Method POST is not allowed on Order List View")
        self.update(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        try:
            return super(OrderView, self).list(request, *args, **kwargs)
        except OrderModel.DoesNotExist:
            raise NotFound("No orders have been found for the current user.")

    def retrieve(self, request, *args, **kwargs):
        try:
            return super(OrderView, self).retrieve(request, *args, **kwargs)
        except OrderModel.DoesNotExist:
            raise NotFound("No order has been found for the current user.")
