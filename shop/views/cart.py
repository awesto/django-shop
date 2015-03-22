# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_by_path
from rest_framework.decorators import list_route
from rest_framework import viewsets
from shop import settings as shop_settings
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


class CheckoutViewSet(BaseViewSet):
    serializer_label = 'checkout'
    serializer_class = serializers.CheckoutSerializer
    item_serializer_class = None

    def __init__(self, **kwargs):
        super(CheckoutViewSet, self).__init__(**kwargs)
        self.checkout_forms = []
        for form_class in shop_settings.CHECKOUT_FORMS:
            self.checkout_forms.append(import_by_path(form_class))

    @list_route(methods=['post'], url_path='update')
    def update(self, request):
        """
        During checkout, a customer can chose from different shipping and payment options, which
        themselves have an influence on the final total. Therefore the cart modifiers must run
        after each of those changes.
        """
        cart = self.get_queryset()
        errors = {}
        for FormClass in self.checkout_forms:
            data = request.data.pop(FormClass.identifier, None)
            if data:
                reply = FormClass.update_model(request, data, cart)
                if isinstance(reply, dict):
                    errors.update(reply)
        cart.save()

        # add possible form errors for giving feedback to the customer
        response = self.list(request)
        response.data.update(errors=errors)
        return response

    @list_route(methods=['post'], url_path='purchase')
    def purchase(self, request):
        response = self.list(request)
        return response
