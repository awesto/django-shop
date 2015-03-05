# -*- coding: utf-8 -*-
from django.db import models
from django.utils.cache import add_never_cache_headers
from rest_framework import serializers, viewsets
from shop.models.cart import BaseCart, BaseCartItem, BaseProduct
from shop.rest.money import MoneyField
from shop.rest.serializers import ProductSummarySerializerBase, ExtraCartRowList


CartModel = getattr(BaseCart, 'MaterializedModel')
CartItemModel = getattr(BaseCartItem, 'MaterializedModel')


class CartListSerializer(serializers.ListSerializer):
    """
    This serializes a list of cart items, whose quantity is non-zero.
    """
    def get_attribute(self, instance):
        manager = super(CartListSerializer, self).get_attribute(instance)
        assert isinstance(manager, models.Manager) and issubclass(manager.model, BaseCartItem)
        return manager.filter(quantity__gt=0)


class WatchListSerializer(serializers.ListSerializer):
    """
    This serializes a list of cart items, whose quantity is zero. Thus these items are considered
    to be in the watch list, which effectively is the cart.
    """
    def get_attribute(self, instance):
        manager = super(WatchListSerializer, self).get_attribute(instance)
        assert isinstance(manager, models.Manager) and issubclass(manager.model, BaseCartItem)
        return manager.filter(quantity=0)


class ProductSummarySerializer(ProductSummarySerializerBase):
    # TODO: see if we can reuse the existing ProductSummarySerializer
    class Meta:
        model = getattr(BaseProduct, 'MaterializedModel')
        fields = ('name', 'identifier', 'price', 'availability', 'product_url', 'product_type',
                  'product_model', 'html', 'description')


class BaseItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='shop-api:cart-detail')
    line_total = MoneyField()
    details = ProductSummarySerializer(source='product', read_only=True)
    extra_rows = ExtraCartRowList(read_only=True)

    class Meta:
        model = CartItemModel

    def validate_product(self, product):
        if not product.active:
            msg = "Product `{}` is inactive, and can not be added to the cart."
            raise serializers.ValidationError(msg.format(product))
        return product

    def create(self, validated_data):
        validated_data['cart'] = CartModel.objects.get_from_request(self.context['request'])
        cart_item, _ = CartItemModel.objects.get_or_create(**validated_data)
        cart_item.save()
        return cart_item

    def to_representation(self, cart_item):
        if cart_item.is_dirty:
            cart_item.update(self.context['request'])
        representation = super(BaseItemSerializer, self).to_representation(cart_item)
        return representation


class CartItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        list_serializer_class = CartListSerializer
        exclude = ('cart', 'id',)


class WatchItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        list_serializer_class = WatchListSerializer
        fields = ('url', 'details', 'quantity',)


class BaseCartSerializer(serializers.ModelSerializer):
    subtotal = MoneyField()
    total = MoneyField()
    extra_rows = ExtraCartRowList(read_only=True)

    class Meta:
        model = CartModel

    def to_representation(self, cart):
        if cart.is_dirty:
            cart.update(self.context['request'])
        self.context['serializer_name'] = 'cart'
        representation = super(BaseCartSerializer, self).to_representation(cart)
        return representation


class CartSerializer(BaseCartSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta(BaseCartSerializer.Meta):
        fields = ('items', 'subtotal', 'extra_rows', 'total',)


class WatchSerializer(BaseCartSerializer):
    items = WatchItemSerializer(many=True, read_only=True)

    class Meta(BaseCartSerializer.Meta):
        fields = ('items',)


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
        kwargs['context'] = self.get_serializer_context()
        many = kwargs.pop('many', False)
        if many:
            return self.serializer_class(*args, **kwargs)
        return self.item_serializer_class(*args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        """Set HTTP headers to not cache this view"""
        if self.action != 'render_product_summary':
            add_never_cache_headers(response)
        return super(BaseViewSet, self).finalize_response(request, response, *args, **kwargs)


class CartViewSet(BaseViewSet):
    serializer_class = CartSerializer
    item_serializer_class = CartItemSerializer


class WatchViewSet(BaseViewSet):
    serializer_class = WatchSerializer
    item_serializer_class = WatchItemSerializer
