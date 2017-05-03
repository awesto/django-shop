# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from shop.models.product import ProductModel
from shop.money.fields import MoneyField
from shop.dashboard.fields import AmountField, FileField, ImageField, TextField


class DashboardModelSerializer(serializers.ModelSerializer):
    """
    Modified implementation of a DRF `ModelSerializer`, which maps the model fields to different
    implementations of serializer fields.
    """
    serializer_field_mapping = dict(serializers.ModelSerializer.serializer_field_mapping)
    serializer_field_mapping.update({
        models.FileField: FileField,
        models.ImageField: ImageField,
        models.TextField: TextField,
        MoneyField: AmountField,
    })


class ProductListSerializer(DashboardModelSerializer):
    price = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()

    class Meta:
        model = ProductModel
        fields = ['id', 'product_name', 'product_code', 'price', 'active']

    def get_product_code(self, product):
        return getattr(product, 'product_code', _("n.a."))

    def get_price(self, product):
        price = product.get_price(self.context['request'])
        return localize(price)


class ProductDetailSerializer(DashboardModelSerializer):
    """
    Default serializer for standard products. Replace this in the merchant implementation
    implementing the class `ProductsDashboard` with a specialized serializer, in case
    the product model does not contain a `unit_price` field.
    """
    unit_price = AmountField()
    active = serializers.BooleanField(default=True, label=_("Active"))

    class Meta:
        model = ProductModel
        fields = '__all__'


class InlineListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        item_mapping = {item.id: item for item in getattr(instance, self.field_name).all()}

        items, data_mapping = [], []
        for data in validated_data:
            if 'id' in data:
                # perform updates
                data_mapping.append(data['id'])
                item = item_mapping.get(data['id'])
                items.append(self.child.update(item, data))
            else:
                # perform creations
                data.update(product=self.parent.instance)
                items.append(self.child.create(data))

        # perform deletions
        for item_id, item in item_mapping.items():
            if item_id not in data_mapping:
                item.delete()

        return items
