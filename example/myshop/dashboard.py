# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.compat import set_many
from rest_framework.utils import model_meta

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


class SmartPhoneVariantListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        variant_mapping = {variant.id: variant for variant in getattr(instance, self.field_name).all()}
        data_mapping = {item['id']: item for item in validated_data}

        # Perform creations and updates.
        variants = []
        for variant_id, data in data_mapping.items():
            variant = variant_mapping.get(variant_id)
            if variant is None:
                variants.append(self.child.create(data))
            else:
                variants.append(self.child.update(variant, data))

        # Perform deletions.
        for variant_id, variant in variant_mapping.items():
            if variant_id not in data_mapping:
                variant.delete()

        return variants


class SmartPhoneVariantSerializer(serializers.ModelSerializer):
    unit_price = AmountField()

    class Meta:
        model = SmartPhoneVariant
        list_serializer_class = SmartPhoneVariantListSerializer
        #fields = '__all__'
        exclude = ['product']
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
            },
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
        # handle nested serialized data
        #for attr, serializer_field in self.fields.items():
        #    if isinstance(serializer_field, serializers.ListSerializer):
        #        instance.variants = serializer_field.update(instance, self.data[attr])

        # pilfered from super method
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


        # handle nested serialized data
        for key, serializer_field in self.fields.items():
            if isinstance(serializer_field, serializers.ListSerializer):
                instance.variants = serializer_field.update(instance, self.data[key])
            else:
                serializer_field.setattr(key, validated_data[key])
        # smart_phone_variants = validated_data.pop('variants')
        # for variant_data in smart_phone_variants:
        #     pk = variant_data.pop('id', None)
        #     product_code = variant_data.get('product_code')
        #     qs = SmartPhoneVariant._default_manager.filter(product_code=product_code)
        #     if pk:
        #         if SmartPhoneVariant._default_manager.exclude(pk=pk).exists():
        #             raise ValidationError(self.message, code='unique')
        #         SmartPhoneVariant.objects.create(product=instance, **variant_data)
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
