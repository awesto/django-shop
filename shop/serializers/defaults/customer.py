# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from shop.serializers.bases import BaseCustomerSerializer


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
