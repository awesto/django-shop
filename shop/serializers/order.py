# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from rest_framework import serializers

from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.models.order import OrderModel
from shop.rest.money import MoneyField


class OrderListSerializer(serializers.ModelSerializer):
    number = serializers.CharField(
        source='get_number',
        read_only=True,
    )

    url = serializers.URLField(
        source='get_absolute_url',
        read_only=True,
    )

    status = serializers.CharField(
        source='status_name',
        read_only=True,
    )

    subtotal = MoneyField()
    total = MoneyField()

    class Meta:
        model = OrderModel
        fields = ['number', 'url', 'created_at', 'updated_at', 'subtotal', 'total', 'status',
                  'shipping_address_text', 'billing_address_text']  # TODO: these fields are not part of the base model
        read_only_fields = ['shipping_address_text', 'billing_address_text']


class OrderDetailSerializer(OrderListSerializer):
    items = app_settings.ORDER_ITEM_SERIALIZER(
        many=True,
        read_only=True,
    )

    extra = serializers.DictField(read_only=True)
    amount_paid = MoneyField(read_only=True)
    outstanding_amount = MoneyField(read_only=True)
    cancelable = serializers.BooleanField(read_only=True)

    is_partially_paid = serializers.SerializerMethodField(
        method_name='get_partially_paid',
        help_text="Returns true, if order has been partially paid",
    )

    annotation = serializers.CharField(
        write_only=True,
        required=False,
    )

    reorder = serializers.BooleanField(
        write_only=True,
        default=False,
    )

    cancel = serializers.BooleanField(
        write_only=True,
        default=False,
    )

    class Meta:
        model = OrderModel
        exclude = ['id', 'customer', 'stored_request', '_subtotal', '_total']
        read_only_fields = ['shipping_address_text', 'billing_address_text']  # TODO: not part of OrderBase

    def get_partially_paid(self, order):
        return order.amount_paid > 0

    def update(self, order, validated_data):
        order.extra.setdefault('addenum', [])
        if validated_data.get('annotation'):
            timestamp = timezone.now().isoformat()
            order.extra['addenum'].append((timestamp, validated_data['annotation']))
            order.save()
        if validated_data['reorder'] is True:
            cart = CartModel.objects.get_from_request(self.context['request'])
            order.readd_to_cart(cart)
        if validated_data['cancel'] is True and order.cancelable():
            order.cancel_order()
            order.save()
        return order
