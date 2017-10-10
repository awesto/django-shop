# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from shop.forms.checkout import (
    ShippingAddressForm, BillingAddressForm, CustomerForm, ShippingMethodForm, PaymentMethodForm, ExtraAnnotationForm)
from .cart import CartSerializer


class CheckoutSerializer(serializers.Serializer):
    cart = serializers.SerializerMethodField()
    customer_tag = serializers.SerializerMethodField()
    shipping_address_tag = serializers.SerializerMethodField()
    billing_address_tag = serializers.SerializerMethodField()
    shipping_method_tag = serializers.SerializerMethodField()
    payment_method_tag = serializers.SerializerMethodField()
    extra_annotation_tag = serializers.SerializerMethodField()

    def get_cart(self, cart):
        serializer = CartSerializer(cart, context=self.context, label='cart')
        return serializer.data

    def get_customer_tag(self, cart):
        try:
            form = CustomerForm(instance=cart.customer)
            return form.as_text()
        except AttributeError:
            return

    def get_shipping_address_tag(self, cart):
        try:
            form = ShippingAddressForm(instance=cart.shipping_address, cart=cart)
            return form.as_text()
        except AttributeError:
            return

    def get_billing_address_tag(self, cart):
        try:
            form = BillingAddressForm(instance=cart.billing_address, cart=cart)
            return form.as_text()
        except AttributeError:
            return

    def get_shipping_method_tag(self, cart):
        try:
            form = ShippingMethodForm(initial=cart.extra, cart=cart)
            return form.as_text()
        except AttributeError:
            return

    def get_payment_method_tag(self, cart):
        try:
            form = PaymentMethodForm(initial=cart.extra, cart=cart)
            return form.as_text()
        except AttributeError:
            return

    def get_extra_annotation_tag(self, cart):
        try:
            form = ExtraAnnotationForm(initial=cart.extra, cart=cart)
            return form.as_text()
        except AttributeError:
            return
