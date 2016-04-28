# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop import deferred
from shop.models.address import BaseShippingAddress, BaseBillingAddress
from shop.models.cart import BaseCart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    shipping_address = deferred.ForeignKey(BaseShippingAddress, null=True, default=None, related_name='+')
    billing_address = deferred.ForeignKey(BaseBillingAddress, null=True, default=None, related_name='+')
