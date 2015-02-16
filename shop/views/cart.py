# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from rest_framework import serializers, viewsets
from rest_framework.decorators import detail_route
from shop.models.cart import BaseCart, BaseCartItem
from shop.models.product import BaseProduct
from shop.serializers.product import BaseProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='shop-api:cart-detail')
    line_subtotal = serializers.CharField(read_only=True)
    line_total = serializers.CharField(read_only=True)
    current_total = serializers.CharField(read_only=True)
    details = BaseProductSerializer(source='product', read_only=True)

    class Meta:
        model = getattr(BaseCartItem, 'MaterializedModel')
        exclude = ('cart', 'id',)

    CartModel = getattr(BaseCart, 'MaterializedModel')
    CartItemModel = getattr(BaseCartItem, 'MaterializedModel')

    def create(self, validated_data):
        validated_data['cart'] = self.CartModel.objects.get_from_request(self.context['request'])
        cart_item, _ = self.CartItemModel.objects.get_or_create(**validated_data)
        cart_item.save()
        return cart_item

    def to_representation(self, cart_item):
        if cart_item.is_dirty:
            cart_item.update(self.context['request'])
        representation = super(CartItemSerializer, self).to_representation(cart_item)
        return representation


class CartSerializer(serializers.ModelSerializer):
    subtotal_price = serializers.CharField()
    total_price = serializers.CharField()
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = getattr(BaseCart, 'MaterializedModel')
        fields = ('items', 'subtotal_price', 'total_price',)

    def to_representation(self, cart):
        if cart.is_dirty:
            cart.update(self.context['request'])
        representation = super(CartSerializer, self).to_representation(cart)
        return representation


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = None  # otherwise DRF complains
    queryset = getattr(BaseCartItem, 'MaterializedModel').objects.all()

    def get_queryset(self):
        cart = getattr(BaseCart, 'MaterializedModel').objects.get_from_request(self.request)
        if self.kwargs.get(self.lookup_field):
            # we're interest only into a certain cart item
            return self.queryset.filter(cart=cart)
        # otherwise the CartSerializer will list all its items
        return cart

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        many = kwargs.pop('many', False)
        if many:
            return CartSerializer(*args, **kwargs)
        return CartItemSerializer(*args, **kwargs)

    @detail_route(url_path='render-item-template')
    def render_item_template(self, request, pk=None, **kwargs):
        """
        Return the AngularJS template to render the cart item for this product type.
        """
        cart_item = self.get_object()
        product = getattr(BaseProduct, 'MaterializedModel').objects.get(pk=cart_item.product_id)
        template = product.get_cart_item_template()
        context = RequestContext(request, {'cart_item': cart_item, 'product': product})
        return render_to_response(template, context)
