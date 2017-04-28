# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shop.views import dashboard
from shop.views.dashboard import router
from shop.rest.fields import AmountField

from myshop.models import Product, SmartCard, SmartPhoneModel, SmartPhoneVariant


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_code', 'price', 'active']

    def get_product_code(self, product):
        return getattr(product, 'product_code', _("n.a."))

    def get_price(self, product):
        price = product.get_price(self.context['request'])
        return localize(price)


class SmartCardSerializer(serializers.ModelSerializer):
    unit_price = AmountField()

    class Meta:
        model = SmartCard
        fields = '__all__'


class SmartPhoneVariantSerializer(serializers.ModelSerializer):
    unit_price = AmountField()

    class Meta:
        model = SmartPhoneVariant
        fields = '__all__'
        extra_kwargs = {
            'product_code': {
                'validators': [],
            }
        }

    def validate(self, data):
        return super(SmartPhoneVariantSerializer, self).validate(data)


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
        smart_phone_variants = validated_data.pop('variants')
        for variant_data in smart_phone_variants:
            pk = variant_data.pop('id', None)
            product_code = variant_data.get('product_code')
            qs = SmartPhoneVariant._default_manager.filter(product_code=product_code)
            if pk:
                if SmartPhoneVariant._default_manager.exclude(pk=pk).exists():
                    raise ValidationError(self.message, code='unique')
                SmartPhoneVariant.objects.create(product=instance, **variant_data)
        return instance


class ProductsDashboard(dashboard.ProductsDashboard):
    list_display = ['product_name', 'product_code', 'price', 'active']
    list_display_links = ['product_name']
    list_serializer_class = ProductListSerializer
    detail_serializer_classes = {
        'myshop.smartcard': SmartCardSerializer,
        'myshop.smartphonemodel': SmartPhoneSerializer,
    }

router.register('products', ProductsDashboard)
