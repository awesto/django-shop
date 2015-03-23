# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from jsonfield.fields import JSONField
from shop.models import deferred
from shop.models.address import BaseAddress
from shop.models.cart import BaseCart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    shipping_address = deferred.ForeignKey(BaseAddress, null=True, default=None, related_name='+')
    invoice_address = deferred.ForeignKey(BaseAddress, null=True, default=None, related_name='+')
    payment_method = JSONField(blank=True, null=True)
    shipping_method = JSONField(blank=True, null=True)
    extras = JSONField(blank=True, null=True)
