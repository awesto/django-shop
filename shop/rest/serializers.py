# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.core import exceptions
from django.core.cache import cache
from django.db import models
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.six import with_metaclass
from django.utils.html import strip_spaces_between_tags
from django.utils.formats import localize
from django.utils.safestring import mark_safe, SafeText
from django.utils.translation import get_language_from_request
from rest_framework import serializers
from rest_framework.fields import empty
from shop import settings as shop_settings
from shop.models.cart import CartModel, CartItemModel, BaseCartItem
from shop.models.product import ProductModel
from shop.models.customer import CustomerModel
from shop.models.order import OrderModel, OrderItemModel
from shop.rest.money import MoneyField


class ProductCommonSerializer(serializers.ModelSerializer):
    """
    Common serializer for the Product model, both for the ProductSummarySerializer and the
    ProductDetailSerializer.
    """
    price = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    def get_price(self, product):
        price = product.get_price(self.context['request'])
        return localize(price)

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
        request = self.context['request']
        cache_key = 'product:{0}|{1}-{2}-{3}-{4}-{5}'.format(product.id, app_label, self.label,
            product.product_model, postfix, get_language_from_request(request))
        content = cache.get(cache_key)
        if content:
            return mark_safe(content)
        params = [
            (app_label, self.label, product.product_model, postfix),
            (app_label, self.label, 'product', postfix),
            ('shop', self.label, 'product', postfix),
        ]
        try:
            template = select_template(['{0}/products/{1}-{2}-{3}.html'.format(*p) for p in params])
        except TemplateDoesNotExist:
            return SafeText("<!-- no such template: '{0}/products/{1}-{2}-{3}.html' -->".format(*params[0]))
        # when rendering emails, we require an absolute URI, so that media can be accessed from
        # the mail client
        absolute_base_uri = request.build_absolute_uri('/').rstrip('/')
        context = RequestContext(request, {'product': product, 'ABSOLUTE_BASE_URI': absolute_base_uri})
        content = strip_spaces_between_tags(template.render(context).strip())
        cache.set(cache_key, content, shop_settings.CACHE_DURATIONS['product_html_snippet'])
        return mark_safe(content)


class SerializerRegistryMetaclass(serializers.SerializerMetaclass):
    """
    Keep a global reference onto the class implementing `ProductSummarySerializerBase`.
    There can be only one class instance, because the products summary is the lowest common
    denominator for all products of this shop instance. Otherwise we would be unable to mix
    different polymorphic product types in the Catalog, Cart and Order list views.
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
"""
Global reference to the common ProductSerializer
"""


class ProductSummarySerializerBase(with_metaclass(SerializerRegistryMetaclass, ProductCommonSerializer)):
    """
    Serialize a summary of the polymorphic Product model, suitable for Catalog List Views,
    Cart List Views and Order List Views.
    """
    product_url = serializers.URLField(source='get_absolute_url', read_only=True)
    product_type = serializers.CharField(read_only=True)
    product_model = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', 'catalog')
        super(ProductSummarySerializerBase, self).__init__(*args, **kwargs)


class ProductDetailSerializerBase(ProductCommonSerializer):
    """
    Serialize all fields of the Product model, for the products detail view.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label', 'catalog')
        super(ProductDetailSerializerBase, self).__init__(*args, **kwargs)

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
    extra = serializers.DictField(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        context = kwargs.get('context', {})
        if 'product' in context:
            instance = self.get_instance(context, data, kwargs)
            if data == empty:
                quantity = self.fields['quantity'].default
            else:
                quantity = self.fields['quantity'].to_internal_value(data['quantity'])
            instance.setdefault('quantity', quantity)
            instance.setdefault('subtotal', instance['quantity'] * instance['unit_price'])
            super(AddToCartSerializer, self).__init__(instance, data, context=context)
        else:
            super(AddToCartSerializer, self).__init__(instance, data, **kwargs)

    def get_instance(self, context, data, extra_args):
        product = context['product']
        return {
            'product': product.id,
            'unit_price': product.get_price(context['request']),
        }


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
        serializer = product_summary_serializer_class(cart_item.product, context=self.context,
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
        serializer = BaseCartSerializer(instance, context=self.context, label='cart')
        return serializer.data


class CustomerSerializer(serializers.ModelSerializer):
    salutation = serializers.CharField(source='get_salutation_display')

    class Meta:
        model = CustomerModel
        fields = ('salutation', 'first_name', 'last_name', 'email', 'extra',)


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = MoneyField()
    unit_price = MoneyField()
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")

    class Meta:
        model = OrderItemModel
        exclude = ('id',)

    def get_summary(self, order_item):
        label = self.context.get('render_label', 'order')
        serializer = product_summary_serializer_class(order_item.product, context=self.context,
                                                      read_only=True, label=label)
        return serializer.data


class OrderListSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='get_number', read_only=True)
    customer = CustomerSerializer(read_only=True)
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    status = serializers.CharField(source='status_name', read_only=True)
    subtotal = MoneyField()
    total = MoneyField()
    extra = serializers.DictField(read_only=True)

    class Meta:
        model = OrderModel
        exclude = ('id', 'stored_request', '_subtotal', '_total',)


class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    amount_paid = MoneyField(read_only=True)
    outstanding_amount = MoneyField(read_only=True)
    is_partially_paid = serializers.SerializerMethodField(method_name='get_partially_paid',
        help_text="Returns true, if order has been partially paid")
    annotation = serializers.CharField(write_only=True, required=False)
    reorder = serializers.BooleanField(write_only=True, default=False)

    def get_partially_paid(self, order):
        return order.amount_paid > 0

    def update(self, order, validated_data):
        order.extra.setdefault('addenum', [])
        if validated_data.get('annotation'):
            timestamp = timezone.now().isoformat()
            order.extra['addenum'].append((timestamp, validated_data['annotation']))
        if validated_data.get('reorder'):
            cart = CartModel.objects.get_from_request(self.context['request'])
            order.readd_to_cart(cart)
        order.save()
        return order


class ProductSelectSerializer(serializers.ModelSerializer):
    """
    A simple serializer to convert the product's name and code for rendering the select widget
    when looking up for a product.
    """
    text = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ('id', 'text',)

    def get_text(self, instance):
        return instance.product_name
