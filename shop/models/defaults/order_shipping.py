# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models import order


class OrderShipping(order.BaseOrderShipping):
    """Default materialized model for OrderShipping"""
