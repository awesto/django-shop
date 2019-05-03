# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.conf import app_settings
from shop.models.cart import CartModel, CartItemModel
from shop.rest.money import MoneyField
from shop.models.fields import ChoiceEnum


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


class BaseItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(lookup_field='pk', view_name='shop:cart-detail')
    unit_price = MoneyField()
    line_total = MoneyField()
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")
    extra_rows = ExtraCartRowList(read_only=True)

    class Meta:
        model = CartItemModel

    def create(self, validated_data):
        assert 'cart' in validated_data
        cart_item = CartItemModel.objects.get_or_create(**validated_data)[0]
        cart_item.save()
        return cart_item

    def to_representation(self, cart_item):
        cart_item.update(self.context['request'])
        representation = super(BaseItemSerializer, self).to_representation(cart_item)
        return representation

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
        exclude = ['cart', 'id']

    def create(self, validated_data):
        validated_data['cart'] = CartModel.objects.get_or_create_from_request(self.context['request'])
        return super(CartItemSerializer, self).create(validated_data)


class WatchItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        fields = ['product', 'product_code', 'url', 'summary', 'quantity', 'extra']

    def create(self, validated_data):
        cart = CartModel.objects.get_or_create_from_request(self.context['request'])
        validated_data.update(cart=cart, quantity=0)
        return super(WatchItemSerializer, self).create(validated_data)


class CartItems(ChoiceEnum):
    without = False
    unsorted = 1
    arranged = 2


class BaseCartSerializer(serializers.ModelSerializer):
    subtotal = MoneyField()
    total = MoneyField()
    extra_rows = ExtraCartRowList(read_only=True)

    class Meta:
        model = CartModel
        fields = ['subtotal', 'total', 'extra_rows']

    def to_representation(self, cart):
        cart.update(self.context['request'])
        representation = super(BaseCartSerializer, self).to_representation(cart)
        if self.with_items:
            items = self.represent_items(cart)
            representation.update(items=items)
        return representation

    def represent_items(self, cart):
        raise NotImplementedError("{} must implement method `represent_items()`.".format(self.__class__))


class CartSerializer(BaseCartSerializer):
    total_quantity = serializers.IntegerField()
    num_items = serializers.IntegerField()

    class Meta(BaseCartSerializer.Meta):
        fields = ['total_quantity', 'num_items'] + BaseCartSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        self.with_items = kwargs.pop('with_items', CartItems.without)
        super(CartSerializer, self).__init__(*args, **kwargs)

    def represent_items(self, cart):
        if self.with_items == CartItems.unsorted:
            items = CartItemModel.objects.filter(cart=cart, quantity__gt=0).order_by('-updated_at')
        else:
            items = CartItemModel.objects.filter_cart_items(cart, self.context['request'])
        serializer = CartItemSerializer(items, context=self.context, label=self.label, many=True)
        return serializer.data


class WatchSerializer(BaseCartSerializer):
    num_items = serializers.IntegerField()

    class Meta(BaseCartSerializer.Meta):
        fields = ['num_items']

    def __init__(self, *args, **kwargs):
        self.with_items = kwargs.pop('with_items', CartItems.arranged)
        super(WatchSerializer, self).__init__(*args, **kwargs)

    def represent_items(self, cart):
        if self.with_items == CartItems.unsorted:
            items = CartItemModel.objects.filter(cart=cart, quantity=0).order_by('-updated_at')
        else:
            items = CartItemModel.objects.filter_watch_items(cart, self.context['request'])
        serializer = WatchItemSerializer(items, context=self.context, label=self.label, many=True)
        return serializer.data
