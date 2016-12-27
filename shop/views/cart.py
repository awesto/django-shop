# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.query import QuerySet
from django.utils.cache import add_never_cache_headers
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from shop.models.cart import CartModel, CartItemModel
from shop.serializers.cart import CartSerializer, CartItemSerializer, WatchSerializer, WatchItemSerializer


class BaseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        try:
            cart = CartModel.objects.get_from_request(self.request)
            if self.kwargs.get(self.lookup_field):
                # we're interest only into a certain cart item
                return CartItemModel.objects.filter(cart=cart)
            # otherwise the CartSerializer will show its detail view and list all its cart items
            return cart
        except CartModel.DoesNotExist:
            return CartModel()

    def paginate_queryset(self, queryset):
        if isinstance(queryset, QuerySet):
            return super(BaseViewSet, self).paginate_queryset(queryset)

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
    serializer_class = CartSerializer
    item_serializer_class = CartItemSerializer

    @list_route(methods=['get'])
    def update_caption(self, request):
        cart = self.get_queryset()
        if cart:
            cart.update(request)
            caption = cart.get_caption_data()
        else:
            caption = CartModel.get_default_caption_data()
        return Response(caption)


class WatchViewSet(BaseViewSet):
    serializer_label = 'watch'
    serializer_class = WatchSerializer
    item_serializer_class = WatchItemSerializer
