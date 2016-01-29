# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models import deferred, order


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""
    quantity = models.IntegerField(_("Ordered quantity"))
    shipped_with = deferred.ForeignKey(order.BaseOrderShipping, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("Shipped with"),
        help_text=_("Refer to the delivery provider used to ship this item"))
