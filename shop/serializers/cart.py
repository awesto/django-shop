# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from rest_framework import serializers

from shop.conf import app_settings
from shop.models.cart import CartModel, CartItemModel, BaseCartItem
from shop.rest.money import MoneyField


class ExtraCartRow(serializers.Serializer):
    """
    This data structure holds extra information for each item, or for the whole cart, while
    processing the cart using their modifiers.
    """
    label = serializers.CharField(
        read_only=True,
        help_text="A short description of this row in a natural language.",
    )

    amount = MoneyField(
        help_text="The price difference, if applied.",
    )


class ExtraCartRowList(serializers.Serializer):
    """
    Represent the OrderedDict used for cart.extra_rows and cart_item.extra_rows.
    Additionally add the modifiers identifier to each element.
    """
    def to_representation(self, obj):
        return [dict(ecr.data, modifier=modifier) for modifier, ecr in obj.items()]


class CartListSerializer(serializers.ListSerializer):
    """
    This serializes a list of cart items, whose quantity is non-zero.
    """
    def get_attribute(self, instance):
        manager = super(CartListSerializer, self).get_attribute(instance)
        assert isinstance(manager, models.Manager) and issubclass(manager.model, BaseCartItem)
        return manager.filter_cart_items(instance, self.context['request'])


class WatchListSerializer(serializers.ListSerializer):
    """
    This serializes a list of cart items, whose quantity is zero. An item in the cart with quantity
    zero is considered as being watched. Thus we can reuse the cart as watch-list without having
    to implement another model.
    """
    def get_attribute(self, instance):
        manager = super(WatchListSerializer, self).get_attribute(instance)
        assert isinstance(manager, models.Manager) and issubclass(manager.model, BaseCartItem)
        return manager.filter_watch_items(instance, self.context['request'])


class ItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItemModel

    def create(self, validated_data):
        assert 'cart' in validated_data
        cart_item = CartItemModel.objects.get_or_create(**validated_data)[0]
        cart_item.save()
        return cart_item

    def to_representation(self, cart_item):
        cart_item.update(self.context['request'])
        representation = super(ItemModelSerializer, self).to_representation(cart_item)
        return representation


class BaseItemSerializer(ItemModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='shop:cart-detail')
    unit_price = MoneyField()
    line_total = MoneyField()
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")
    extra_rows = ExtraCartRowList(read_only=True)

    def validate_product(self, product):
        if not product.active:
            msg = "Product `{}` is inactive, and can not be added to the cart."
            raise serializers.ValidationError(msg.format(product))
        return product

    def get_summary(self, cart_item):
        serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
        serializer = serializer_class(cart_item.product, context=self.context,
                                      read_only=True, label=self.root.label)
        return serializer.data


class CartItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        list_serializer_class = CartListSerializer
        exclude = ('cart', 'id',)

    def create(self, validated_data):
        validated_data['cart'] = CartModel.objects.get_or_create_from_request(self.context['request'])
        return super(CartItemSerializer, self).create(validated_data)


class WatchItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        list_serializer_class = WatchListSerializer
        fields = ('product', 'url', 'summary', 'quantity', 'extra',)

    def create(self, validated_data):
        cart = CartModel.objects.get_or_create_from_request(self.context['request'])
        validated_data.update(cart=cart, quantity=0)
        return super(WatchItemSerializer, self).create(validated_data)


class BaseCartSerializer(serializers.ModelSerializer):
    subtotal = MoneyField()
    total = MoneyField()
    extra_rows = ExtraCartRowList(read_only=True)

    class Meta:
        model = CartModel
        fields = ('subtotal', 'total', 'extra_rows')

    def to_representation(self, cart):
        cart.update(self.context['request'])
        representation = super(BaseCartSerializer, self).to_representation(cart)
        return representation


class CartSerializer(BaseCartSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.IntegerField()
    num_items = serializers.IntegerField()

    class Meta(BaseCartSerializer.Meta):
        fields = ('items', 'total_quantity', 'num_items') + BaseCartSerializer.Meta.fields


class WatchSerializer(BaseCartSerializer):
    items = WatchItemSerializer(many=True, read_only=True)
    num_items = serializers.IntegerField()

    class Meta(BaseCartSerializer.Meta):
        fields = ('items', 'num_items')

    def to_representation(self, cart):
        # grandparent super
        return super(BaseCartSerializer, self).to_representation(cart)


class CheckoutSerializer(serializers.Serializer):
    cart = serializers.SerializerMethodField()

    def get_cart(self, instance):
        serializer = CartSerializer(instance, context=self.context, label='cart')
        return serializer.data
