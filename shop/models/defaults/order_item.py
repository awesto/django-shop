# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models import order


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""
