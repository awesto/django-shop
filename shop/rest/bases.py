# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.models.customer import CustomerModel


class BaseCustomerSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='get_number')

    class Meta:
        model = CustomerModel
        fields = ('number', 'first_name', 'last_name', 'email')
