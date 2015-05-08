# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import generics, mixins
from rest_framework.renderers import BrowsableAPIRenderer
from shop.rest.serializers import OrderListSerializer, OrderDetailSerializer
from shop.rest.money import JSONRenderer
from shop.rest.renderers import CMSPageRenderer
from shop.models.auth import get_customer
from shop.models.order import OrderModel


class GenericOrderView(generics.GenericAPIView):
    """
    Base View class to render the fulfilled orders for the current user.
    """
    renderer_classes = (CMSPageRenderer, JSONRenderer, BrowsableAPIRenderer)
    thank_you = False  # if true render a "Thank You" view, rather than a normal order object

    def get_queryset(self):
        user = get_customer(self.request)
        return OrderModel.objects.filter(user=user).order_by('-updated_at',)

    def get_renderer_context(self):
        renderer_context = super(GenericOrderView, self).get_renderer_context()
        if renderer_context['request'].accepted_renderer.format == 'html':
            renderer_context.update(many=isinstance(self, mixins.ListModelMixin), thank_you=self.thank_you)
        return renderer_context

    def get_template_names(self):
        return [self.request.current_page.get_template()]


class OrderListView(mixins.ListModelMixin, GenericOrderView):
    serializer_class = OrderListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderRetrieveView(mixins.RetrieveModelMixin, GenericOrderView):
    serializer_class = OrderDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        if self.thank_you:
            return self.get_queryset().last()
        return super(OrderRetrieveView, self).get_object()
