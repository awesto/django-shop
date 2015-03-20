# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.models import order


class Order(order.BaseOrder):
    """Default materialized model for Order"""


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""


class OrderExtraRow(order.BaseOrderExtraRow):
    """Default materialized model for OrderExtraRow"""


class OrderItemExtraRow(order.BaseItemExtraRow):
    """Default materialized model for OrderItemExtraRow"""
