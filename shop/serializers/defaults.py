# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.fields import empty

from shop.conf import app_settings
from shop.models.product import ProductModel
from shop.rest.money import MoneyField
from shop.serializers.bases import BaseCustomerSerializer
from .bases import BaseOrderItemSerializer


class CustomerSerializer(BaseCustomerSerializer):
    """
    If the chosen customer model is the default :class:`shop.models.defaults.Customer`, then this
    serializer shall be used.

    If another customer model is used, then add a customized ``CustomerSerializer`` to your project
    and point your configuration settings ``SHOP_CUSTOMER_SERIALIZER`` onto it.
    """
    salutation = serializers.CharField(source='get_salutation_display', read_only=True)

    class Meta(BaseCustomerSerializer.Meta):
        fields = BaseCustomerSerializer.Meta.fields + ['salutation']


class ProductSelectSerializer(serializers.ModelSerializer):
    """
    A simple serializer to convert the product's name and code for while rendering the `Select2 Widget`_
    when looking up for a product. This serializer shall return a list of 2-tuples, whose 1st entry is the
    primary key of the product and the second entry is the rendered name.

    .. _Select2 Widget: https://github.com/applegrew/django-select2
    """
    text = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ['id', 'text']

    def get_text(self, instance):
        return instance.product_name


class AddToCartSerializer(serializers.Serializer):
    """
    By default, this serializer is used by the view class :class:`shop.views.catalog.AddToCartView`,
    which handles the communication from the "Add to Cart" dialog box.

    This serializer shall be replaced by an alternative implementation, if product variations are used
    on the same catalog's detail view.
    """
    quantity = serializers.IntegerField(default=1, min_value=1)
    unit_price = MoneyField(read_only=True)
    subtotal = MoneyField(read_only=True)
    product = serializers.IntegerField(read_only=True, help_text="The product's primary key")
    product_code = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    extra = serializers.DictField(read_only=True, default={})

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
        """
        Method to store the ordered products in the cart item instance.
        Remember to override this method, if the ``product_code`` is part of the
        variation rather than being part of the product itself.
        """
        product = context['product']
        extra = data.get('extra', {}) if data is not empty else {}
        return {
            'product': product.id,
            'product_code': product.product_code,
            'unit_price': product.get_price(context['request']),
            'extra': extra,
        }


class OrderItemSerializer(BaseOrderItemSerializer):
    summary = serializers.SerializerMethodField(
        help_text="Sub-serializer for fields to be shown in the product's summary.")

    class Meta(BaseOrderItemSerializer.Meta):
        fields = ['line_total', 'unit_price', 'product_code', 'quantity', 'summary', 'extra']

    def get_summary(self, order_item):
        label = self.context.get('render_label', 'order')
        serializer_class = app_settings.PRODUCT_SUMMARY_SERIALIZER
        serializer = serializer_class(order_item.product, context=self.context,
                                      read_only=True, label=label)
        return serializer.data
