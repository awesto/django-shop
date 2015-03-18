# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.cache import add_never_cache_headers
from rest_framework.decorators import detail_route, list_route
from rest_framework import viewsets
from shop.models.cart import CartModel, CartItemModel
from shop.rest import serializers
from shop.forms.address import AddressForm
from shop.forms.auth import CustomerForm


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
        pass

    @list_route()
    def summary(self, request):
        return self.list(request)

    @list_route(methods=['post'], url_path='submit')
    def submit(self, request):
        cart = self.get_queryset()
        errors = {}
        customer = CustomerForm(data=request.data['customer'])
        print customer.instance
        if not customer.is_valid():
            errors[customer.form_name] = dict(customer.errors)
        shipping_address = AddressForm('shipping', data=request.data['shipping_address'])
        if not shipping_address.is_valid():
            errors[shipping_address.form_name] = dict(shipping_address.errors)
        invoice_address = AddressForm('invoice', data=request.data['invoice_address'])
        if not invoice_address.is_valid():
            errors[invoice_address.form_name] = dict(invoice_address.errors)
        response = self.list(request)
        response.data.update(errors=errors)
        return response
