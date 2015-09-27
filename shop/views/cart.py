# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.cache import add_never_cache_headers
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from shop.models.cart import CartModel, CartItemModel
from shop.rest import serializers


class BaseViewSet(viewsets.ModelViewSet):
    paginate_by = None

    def get_queryset(self):
        cart = CartModel.objects.get_from_request(self.request)
        if self.kwargs.get(self.lookup_field):
            # we're interest only into a certain cart item
            return CartItemModel.objects.filter(cart=cart)
        # otherwise the CartSerializer will show its detail and list all its items
        return cart

    @list_route(methods=['get'])
    def count_items(self, request):
        data = {'count_items': self.get_queryset().items.count()}
        return Response(data)

    def get_serializer(self, *args, **kwargs):
        kwargs.update(context=self.get_serializer_context(), label=self.serializer_label)
        many = kwargs.pop('many', False)
        if many or self.item_serializer_class is None:
            return self.serializer_class(*args, **kwargs)
        return self.item_serializer_class(*args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        """Set HTTP headers to not cache this view"""
        if self.action != 'render_product_summary':
            add_never_cache_headers(response)
        return super(BaseViewSet, self).finalize_response(request, response, *args, **kwargs)


class CartViewSet(BaseViewSet):
    serializer_label = 'cart'
    serializer_class = serializers.CartSerializer
    item_serializer_class = serializers.CartItemSerializer


class WatchViewSet(BaseViewSet):
    serializer_label = 'watch'
    serializer_class = serializers.WatchSerializer
    item_serializer_class = serializers.WatchItemSerializer
