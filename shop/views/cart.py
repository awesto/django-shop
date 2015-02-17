# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.cache import add_never_cache_headers
from rest_framework import serializers, viewsets
from rest_framework.decorators import detail_route
from shop.models.cart import BaseCart, BaseCartItem
from shop.models.product import BaseProduct
from shop.serializers.product import BaseProductSerializer

CartModel = getattr(BaseCart, 'MaterializedModel')
CartItemModel = getattr(BaseCartItem, 'MaterializedModel')


class CartItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='shop-api:cart-detail')
    line_subtotal = serializers.CharField(read_only=True)
    line_total = serializers.CharField(read_only=True)
    details = BaseProductSerializer(source='product', read_only=True)

    class Meta:
        model = CartItemModel
        exclude = ('cart', 'id',)


    def validate_product(self, product):
        if not product.get_availability(self.context['request']):
            raise serializers.ValidationError("Product '{0}' can not be added to the cart.".format(product))
        return product

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
        model = CartModel
        fields = ('items', 'subtotal_price', 'total_price',)

    def to_representation(self, cart):
        if cart.is_dirty:
            cart.update(self.context['request'])
        if 'digest' in self.context['request'].query_params:
            # by settings `CartItemSerializer.write_only` to True, we can skip the list serialization
            self.fields['items'].write_only = True
        representation = super(CartSerializer, self).to_representation(cart)
        return representation


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = None  # otherwise DRF complains

    def get_queryset(self):
        cart = CartModel.objects.get_from_request(self.request)
        if self.kwargs.get(self.lookup_field):
            # we're interest only into a certain cart item
        # otherwise the CartSerializer will list all its items
            return CartItemModel.objects.filter(cart=cart)
        return cart

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        many = kwargs.pop('many', False)
        if many:
            return CartSerializer(*args, **kwargs)
        return CartItemSerializer(*args, **kwargs)

    @detail_route(url_path='render-product-summary')
    def render_product_summary(self, request, pk=None, **kwargs):
        """
        Returns a summary of the product, to be rendered as item in the cart.
        """
        cart_item = self.get_object()
        product = getattr(BaseProduct, 'MaterializedModel').objects.get(pk=cart_item.product_id)
        product.price = product.get_price(request)
        product.availability = product.get_availability(request)
        context = RequestContext(request, {'cart_item': cart_item, 'product': product})
        return render_to_response(product.cart_summary_template, context)

    def finalize_response(self, request, response, *args, **kwargs):
        if self.action != 'render_product_summary':
            add_never_cache_headers(response)
        return super(CartViewSet, self).finalize_response(request, response, *args, **kwargs)
