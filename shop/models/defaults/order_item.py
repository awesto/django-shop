# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models import order


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem, which keeps track on shipping"""
    quantity = models.IntegerField(_("Ordered quantity"))
