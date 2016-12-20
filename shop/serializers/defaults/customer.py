# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from shop.rest.bases import BaseCustomerSerializer


class CustomerSerializer(BaseCustomerSerializer):
    salutation = serializers.CharField(source='get_salutation_display')

    class Meta(BaseCustomerSerializer.Meta):
        fields = ('salutation',) + BaseCustomerSerializer.Meta.fields
