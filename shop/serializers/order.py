# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from rest_framework import serializers

from shop import app_settings
from shop.models.cart import CartModel
from shop.models.order import OrderModel
from shop.rest.money import MoneyField


class OrderListSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='get_number', read_only=True)
    customer = app_settings.CUSTOMER_SERIALIZER(read_only=True)
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    status = serializers.CharField(source='status_name', read_only=True)
    subtotal = MoneyField()
    total = MoneyField()
    extra = serializers.DictField(read_only=True)

    class Meta:
        model = OrderModel
        exclude = ('id', 'stored_request', '_subtotal', '_total',)


class OrderDetailSerializer(OrderListSerializer):
    items = app_settings.ORDER_ITEM_SERIALIZER(many=True, read_only=True)
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
