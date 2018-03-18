# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import SET_DEFAULT

from shop import deferred
from shop.models.address import BaseShippingAddress, BaseBillingAddress
from shop.models.cart import BaseCart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    shipping_address = deferred.ForeignKey(
        BaseShippingAddress,
        null=True,
        default=None,
        related_name='+',
        on_delete=SET_DEFAULT,
    )

    billing_address = deferred.ForeignKey(
        BaseBillingAddress,
        null=True,
        default=None,
        related_name='+',
        on_delete=SET_DEFAULT,
    )
