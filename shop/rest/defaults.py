# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .bases import BaseCustomerSerializer


class CustomerSerializer(BaseCustomerSerializer):
    """
    This CustomerSerializer shall be used as a default, if used in combination with
    :class:`shop.models.defaults.customer.CustomerSerializer`.
    Replace it by another serializer, for alternative Customer Models.
    """
    salutation = serializers.CharField(source='get_salutation_display', read_only=True)

    class Meta(BaseCustomerSerializer.Meta):
        fields = BaseCustomerSerializer.Meta.fields + ('salutation',)
