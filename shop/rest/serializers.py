# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from django.core import exceptions
from django.contrib.auth import get_user_model
from django.db import models
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.six import with_metaclass
from django.utils.html import strip_spaces_between_tags
from django.utils.safestring import mark_safe
from jsonfield.fields import JSONField
from rest_framework import serializers
from rest_framework.fields import empty
from shop.models.cart import CartModel, CartItemModel, BaseCartItem
from shop.models.order import OrderModel, OrderItemModel
from shop.rest.money import MoneyField


class OrderedDictField(serializers.Field):
    """
    Serializer field which transparently bypasses the internal representation of an OrderedDict.
    """
    def to_representation(self, obj):
        return OrderedDict(obj)

    def to_internal_value(self, data):
        return OrderedDict(data)


class JSONSerializerField(serializers.Field):
    """
    Serializer field which transparently bypasses its object instead of serializing/deserializing.
    """
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data

# add JSONField to the map of customized serializers
serializers.ModelSerializer._field_mapping[JSONField] = JSONSerializerField


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

    def render_html(self, product, postfix):
        """
        Return a HTML snippet containing a rendered summary for this product.
        Build a template search path with `postfix` distinction.
        """
        if not self.label:
            msg = "The Product Serializer must be configured using a `label` field."
            raise exceptions.ImproperlyConfigured(msg)
        app_label = product._meta.app_label.lower()
        product_type = product.__class__.__name__.lower()
        params = [
            (app_label, self.label, product_type, postfix),
            (app_label, self.label, 'product', postfix),
            ('shop', self.label, 'product', postfix),
        ]
        template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
        request = self.context['request']
        # when rendering emails, we require an absolute URI, so that media can be accessed from
        # the mail client
        absolute_base_uri = request.build_absolute_uri('/').rstrip('/')
        context = RequestContext(request, {'product': product, 'ABSOLUTE_BASE_URI': absolute_base_uri})
        content = strip_spaces_between_tags(template.render(context).strip())
        return mark_safe(content)


class SerializerRegistryMetaclass(serializers.SerializerMetaclass):
    """
    Keep a global reference onto the class implementing `ProductSummarySerializerBase`.
    There can be only one class instance, because the products summary is the lowest common
    denominator for all products of this shop instance.
    """
    def __new__(cls, clsname, bases, attrs):
        global product_summary_serializer_class
        if product_summary_serializer_class:
            msg = "Class `{}` inheriting from `ProductSummarySerializerBase` already registred."
            raise exceptions.ImproperlyConfigured(msg.format(product_summary_serializer_class.__name__))
        new_class = super(cls, SerializerRegistryMetaclass).__new__(cls, clsname, bases, attrs)
        if clsname != 'ProductSummarySerializerBase':
            product_summary_serializer_class = new_class
        return new_class

product_summary_serializer_class = None


class ProductSummarySerializerBase(with_metaclass(SerializerRegistryMetaclass, ProductCommonSerializer)):
    """
    Serialize a summary of the polymorphic Product model, suitable for product list views,
    cart-lists and order-lists.
    """
    product_url = serializers.URLField(source='get_absolute_url', read_only=True)
    product_type = serializers.CharField(read_only=True)
    product_model = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        if not kwargs.get('label'):
            kwargs.update(label='overview')
        super(ProductSummarySerializerBase, self).__init__(*args, **kwargs)


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
            msg = "A context is required for this serializer and must contain the `product` and the `request` object."
            raise ValueError(msg)
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
        return manager.filter(quantity__gt=0)


class WatchListSerializer(serializers.ListSerializer):
    """
    This serializes a list of cart items, whose quantity is zero. An item in the cart with quantity
    zero is considered as being watched. Thus we can reuse the cart as watch-list without having
    to implement another model.
    """
    def get_attribute(self, instance):
        manager = super(WatchListSerializer, self).get_attribute(instance)
        assert isinstance(manager, models.Manager) and issubclass(manager.model, BaseCartItem)
        return manager.filter(quantity=0)


class ItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItemModel

    def create(self, validated_data):
        validated_data['cart'] = CartModel.objects.get_from_request(self.context['request'])
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
        serializer = product_summary_serializer_class(cart_item.product, context=self.context,
                                                      read_only=True, label=self.root.label)
        return serializer.data


class CartItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        list_serializer_class = CartListSerializer
        exclude = ('cart', 'id',)


class WatchItemSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        list_serializer_class = WatchListSerializer
        fields = ('product', 'url', 'summary', 'quantity', 'extra',)

    def create(self, validated_data):
        validated_data['quantity'] = 0
        return super(WatchItemSerializer, self).create(validated_data)


class BaseCartSerializer(serializers.ModelSerializer):
    subtotal = MoneyField()
    total = MoneyField()
    extra_rows = ExtraCartRowList(read_only=True)

    class Meta:
        model = CartModel

    def to_representation(self, cart):
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


class CheckoutSerializer(BaseCartSerializer):
    class Meta(BaseCartSerializer.Meta):
        fields = ('subtotal', 'extra_rows', 'total',)


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = MoneyField()
    unit_price = MoneyField()
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")

    class Meta:
        model = OrderItemModel
        exclude = ('id',)

    def get_summary(self, order_item):
        serializer = product_summary_serializer_class(order_item.product, context=self.context,
                                                      read_only=True, label='order')
        return serializer.data


class OrderSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField()
    subtotal = MoneyField()
    total = MoneyField()

    class Meta:
        model = OrderModel
        exclude = ('id', 'user', 'stored_request', '_subtotal', '_total',)


class OrderListSerializer(OrderSerializer):
    url = serializers.URLField(source='get_absolute_url', read_only=True)


class OrderDetailSerializer(OrderSerializer):
    items = OrderItemSerializer(many=True, read_only=True)


class CustomerSerializer(serializers.ModelSerializer):
    salutation = serializers.CharField(source='get_salutation_display')

    class Meta:
        model = get_user_model()
        fields = ('salutation', 'first_name', 'last_name', 'email', 'extra',)
