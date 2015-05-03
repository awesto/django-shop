# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from shop.rest.serializers import OrderListSerializer, OrderDetailSerializer
from shop.models.order import OrderModel


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user).order_by('-updated_at',)

    def get_serializer(self, *args, **kwargs):
        kwargs.update(context=self.get_serializer_context(), label='order')
        if kwargs.pop('many', False):
            return OrderListSerializer(*args, **kwargs)
        return OrderDetailSerializer(*args, **kwargs)

    @list_route(url_path='last')
    def last_order(self, request):
        qs = self.get_queryset().last()
        if qs:
            serializer = OrderDetailSerializer(qs, context=self.get_serializer_context(), label='order')
            return Response(serializer.data)
        return Response(OrderDetailSerializer.errors, status=HTTP_404_NOT_FOUND)
