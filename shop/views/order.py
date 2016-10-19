# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.cache import never_cache
from rest_framework import generics, mixins
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.exceptions import PermissionDenied
from shop.rest.serializers import OrderListSerializer, OrderDetailSerializer
from shop.rest.money import JSONRenderer
from shop.rest.renderers import CMSPageRenderer
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

    def get_queryset(self):
        return OrderModel.objects.filter_from_request(self.request)

    def get_serializer_class(self):
        if self.many:
            return self.list_serializer_class
        return self.detail_serializer_class

    def get_renderer_context(self):
        renderer_context = super(OrderView, self).get_renderer_context()
        if self.request.accepted_renderer.format == 'html':
            renderer_context['many'] = self.many
            if self.many is False:
                # add an extra ance to the breadcrumb
                try:
                    renderer_context['extra_ance'] = self.get_object().get_number()
                except (AttributeError, PermissionDenied):
                    pass
        return renderer_context

    def get_template_names(self):
        return [self.request.current_page.get_template()]

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
        if self.is_last():
            self.many = False
        if self.many:
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.is_last():
            self.many = False
        if self.many:
            return self.list(request, *args, **kwargs)
        self.update(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    def is_last(self):
        """
        Return true, if the last order shall be rendered.
        Useful to render a Thank-You view immediately after a purchase.
        """
        return self.request.current_page.reverse_id == 'shop-order-last'
