# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import itertools
from django.db import models
from django.template import RequestContext
from django.template.loader import select_template
from rest_framework import serializers
from rest_framework.fields import empty
from shop.models.cart import CartModel, CartItemModel, BaseCartItem
from shop.models.product import ProductModel
from shop.rest.money import MoneyField


class ProductCommonSerializer(serializers.ModelSerializer):
    """
    Common serializer for the Product model, both for the ProductSummarySerializer and the
    ProductDetailSerializer.
    """
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    def get_price(self, product):
        return product.get_price(self.context['request'])

    def get_availability(self, product):
        return product.get_availability(self.context['request'])


class ProductSummarySerializerBase(ProductCommonSerializer):
    """
    Serialize a subset of the Product model, suitable for list views, cart- and order-lists.
    """
    product_url = serializers.CharField(source='get_absolute_url', read_only=True)
    product_type = serializers.CharField(read_only=True)
    product_model = serializers.CharField(read_only=True)
    html = serializers.SerializerMethodField()  # HTML snippet for product's summary

    def find_template(self, product):
        app_label = product._meta.app_label.lower()
        basename = '{}-summary.html'.format(product.__class__.__name__.lower())
        templates = [(app_label, basename), (app_label, 'product-summary.html'), ('shop', 'product-summary.html')]
        if self.root.label:
            # with this label we can distinguish between different serializer instantiations
            prefixed_templates = [(base, self.root.label + '-' + leaf) for base, leaf in templates]
            templates = itertools.chain.from_iterable(zip(prefixed_templates, templates))
        templates = [os.path.join(base, leaf) for base, leaf in templates]
        return select_template(templates)

    def get_html(self, product):
        """
        Return a HTML snippet containing a rendered summary for this product.
        """
        template = self.find_template(product)
        request = self.context['request']
        context = RequestContext(request, {'product': product})
        return template.render(context)


class ProductDetailSerializerBase(ProductCommonSerializer):
    """
    Serialize all fields of the Product model, for the products detail view.
    """
    def to_representation(self, obj):
        product = super(ProductDetailSerializerBase, self).to_representation(obj)
        # add a serialized representation of the product to the context
        return {'product': dict(product)}


class AddToCartSerializer(serializers.Serializer):
    """
    Serialize fields used in the "Add to Cart" dialog box.
    """
    quantity = serializers.IntegerField(default=1, min_value=1)
    unit_price = MoneyField(read_only=True)
    subtotal = MoneyField(read_only=True)
    product = serializers.IntegerField(read_only=True, help_text="The product's primary key")

    def __init__(self, instance=None, data=empty, **kwargs):
        context = kwargs.get('context', {})
        if 'product' not in context or 'request' not in context:
            raise ValueError("A context is required for this serializer and must contain the `product` and the `request` object.")
        instance = {'product': context['product'].id}
        unit_price = context['product'].get_price(context['request'])
        if data == empty:
            quantity = self.fields['quantity'].default
        else:
            quantity = data['quantity']
        instance.update(quantity=quantity, unit_price=unit_price, subtotal=quantity * unit_price)
        super(AddToCartSerializer, self).__init__(instance, data, **kwargs)


class ExtraCartRow(serializers.Serializer):
    """
    This data structure holds extra information for each item, or for the whole cart, while
    processing the cart using their modifiers.
    """
    label = serializers.CharField(read_only=True,
        help_text="A short description of this row in a natural language.")
    amount = MoneyField(read_only=True,
        help_text="The price difference, if applied.")


class ExtraCartRowList(serializers.Serializer):
    """
    Represent a list of `ExtraCartRow`s. Additionally add the modifiers identifier to each element.
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
        model = ProductModel
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
