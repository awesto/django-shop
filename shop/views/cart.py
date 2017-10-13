# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.query import QuerySet
from django.utils.cache import add_never_cache_headers

from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from shop.conf import app_settings
from shop.models.cart import CartModel, CartItemModel
from shop.serializers.cart import (BaseCartSerializer, CartSerializer, CartItemSerializer,
                                   WatchSerializer, WatchItemSerializer)


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

    def update(self, request, *args, **kwargs):
        """
        Handle changing the amount of the cart item referred by its primary key.
        """
        cart_item = self.get_object()
        context = self.get_serializer_context()
        item_serializer = self.item_serializer_class(cart_item, context=context, data=request.data,
                                                     label=self.serializer_label)
        item_serializer.is_valid(raise_exception=True)
        self.perform_update(item_serializer)
        cart_serializer = BaseCartSerializer(cart_item.cart, context=context, label=self.serializer_label)
        response_data = {
            'cart_item': item_serializer.data,
            'cart': cart_serializer.data,
        }
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a cart item referred by its primary key.
        """
        cart_item = self.get_object()
        context = self.get_serializer_context()
        cart_serializer = BaseCartSerializer(cart_item.cart, context=context, label=self.serializer_label)
        self.perform_destroy(cart_item)
        response_data = {
            'cart_item': None,
            'cart': cart_serializer.data,
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

    def finalize_response(self, request, response, *args, **kwargs):
        """Set HTTP headers to not cache this view"""
        if self.action != 'render_product_summary':
            add_never_cache_headers(response)
        return super(BaseViewSet, self).finalize_response(request, response, *args, **kwargs)


class CartViewSet(BaseViewSet):
    serializer_label = 'cart'
    serializer_class = CartSerializer
    item_serializer_class = CartItemSerializer
    caption_serializer_class = app_settings.SHOP_CART_ICON_CAPTION_SERIALIZER

    @list_route(methods=['get'])
    def update_caption(self, request):
        # deprecated
        cart = self.get_queryset()
        if cart:
            cart.update(request)
            caption = cart.get_caption_data()
        else:
            caption = CartModel.get_default_caption_data()
        return Response(caption)

    @list_route(methods=['get'], url_path='fetch-caption')
    def fetch_caption(self, request):
        cart = self.get_queryset()
        if cart:
            cart.update(request)
        serializer = self.caption_serializer_class(instance=cart)
        return Response(data=serializer.data)


class WatchViewSet(BaseViewSet):
    serializer_label = 'watch'
    serializer_class = WatchSerializer
    item_serializer_class = WatchItemSerializer
