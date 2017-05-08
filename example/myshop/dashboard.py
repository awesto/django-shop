# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied

from rest_framework import serializers
from rest_framework.compat import set_many
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.utils import model_meta

from shop.dashboard.serializers import (ProductListSerializer, ProductDetailSerializer,
                                        InlineListSerializer)
from shop.dashboard.viewsets import DashboardViewSet

from myshop.models import SmartCard, SmartPhoneModel, SmartPhoneVariant


class SmartCardSerializer(ProductDetailSerializer):
    class Meta:
        model = SmartCard
        fields = '__all__'


class SmartPhoneVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartPhoneVariant
        list_serializer_class = InlineListSerializer
        fields = '__all__'
        extra_kwargs = {
            'id': {
                'read_only': False,
                'required': False,
                'style': {'hidden': True},
            },
            'product': {
                'required': False,
                'style': {'hidden': True},
            },
            'product_code': {
                'validators': [],
            },
            'unit_price': {
                'coerce_to_string': False,
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
        extra_kwargs = {
            'width': {
                'coerce_to_string': False,
            },
            'height': {
                'coerce_to_string': False,
            },
            'weight': {
                'coerce_to_string': False,
            },
            'screen_size': {
                'coerce_to_string': False,
            },
        }

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


class ProductsViewSet(DashboardViewSet):
    list_display = ['product_name', 'product_code', 'price', 'active']
    list_display_links = ['product_name']
    list_serializer_class = ProductListSerializer
    detail_serializer_classes = {
        'myshop.smartcard': SmartCardSerializer,
        'myshop.smartphonemodel': SmartPhoneSerializer,
    }


from shop.models.defaults.customer import Customer

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['salutation', 'number']


class ProfileViewSet(DashboardViewSet):
    list_serializer_class = ProfileSerializer
    singleton = True

    def __init__(self, *args, **kwargs):
        kwargs.update(suffix='Instance')
        super(ProfileViewSet, self).__init__(*args, **kwargs)

    def get_serializer_class(self):
        return self.list_serializer_class

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer_class()(data=request.data, instance=instance)
        if serializer.is_valid():
            serializer.save()
        # TODO: we should consider a redirect after a successful save
        return Response({'serializer': serializer, 'instance': instance})

    def get_object(self):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        try:
            return Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            raise PermissionDenied
