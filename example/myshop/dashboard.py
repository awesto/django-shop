# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.compat import set_many
from rest_framework.exceptions import ValidationError
from rest_framework.utils import model_meta

from shop.dashboard.router import router
from shop.dashboard.serializers import (ProductListSerializer, ProductDetailSerializer,
                                        InlineListSerializer)
from shop.dashboard.viewsets import ProductsDashboard as BaseProductsDashboard
from shop.rest.fields import AmountField

from myshop.models import SmartCard, SmartPhoneModel, SmartPhoneVariant


class SmartCardSerializer(ProductDetailSerializer):
    class Meta:
        model = SmartCard
        fields = '__all__'


class SmartPhoneVariantSerializer(serializers.ModelSerializer):
    unit_price = AmountField()

    class Meta:
        model = SmartPhoneVariant
        list_serializer_class = InlineListSerializer
        fields = '__all__'
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
            },
            'product': {
                'required': False,
            },
            'product_code': {
                'validators': [],
            }
        }

    def validate_product(self, data):
        if data.pk != self.parent.parent.instance.pk:
            raise ValidationError("Product ID mismatch")
        return data


class SmartPhoneSerializer(serializers.ModelSerializer):
    variants = SmartPhoneVariantSerializer(many=True)

    class Meta:
        model = SmartPhoneModel
        fields = '__all__'

    def validate(self, data):
        data = super(SmartPhoneSerializer, self).validate(data)
        return data

    def is_valid(self, raise_exception=False):
        return super(SmartPhoneSerializer, self).is_valid(raise_exception)

    def create(self, validated_data):
        smart_phone_variants = validated_data.pop('variants')
        instance = SmartPhoneModel.objects.create(**validated_data)
        for variant in smart_phone_variants:
            SmartPhoneVariant.objects.create(product=instance, **variant)
        return instance

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if isinstance(self.fields[attr], serializers.ListSerializer):
                setattr(instance, attr, self.fields[attr].update(instance, value))
            elif attr in info.relations and info.relations[attr].to_many:
                set_many(instance, attr, value)
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance


class ProductsDashboard(BaseProductsDashboard):
    list_display = ['product_name', 'product_code', 'price', 'active']
    list_display_links = ['product_name']
    list_serializer_class = ProductListSerializer
    detail_serializer_classes = {
        'myshop.smartcard': SmartCardSerializer,
        'myshop.smartphonemodel': SmartPhoneSerializer,
    }

router.register('products', ProductsDashboard)
