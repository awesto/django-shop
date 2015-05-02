# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets
from shop.rest.serializers import OrderSerializer, OrderItemSerializer
from shop.models.order import OrderModel


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)

    def X_retrieve(self, request, *args, **kwargs):
        order = super(OrderViewSet, self).retrieve(self, request, *args, **kwargs)
        

    def X_get_serializer(self, *args, **kwargs):
        kwargs.update(context=self.get_serializer_context(), label='order')
        many = kwargs.pop('many', False)
        if many:
            return OrderSerializer(*args, **kwargs)
        return OrderItemSerializer(*args, **kwargs)
