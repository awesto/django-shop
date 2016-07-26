# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models import order


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""
    quantity = models.IntegerField(_("Ordered quantity"))

    def populate_from_cart_item(self, cart_item, request):
        # The optional attribute `product.product_code` might be missing, if for instance
        # it is implemented through a product variation. In this case replace this method
        # by it's own business logic.
        self.product_code = cart_item.product.product_code
        super(OrderItem, self).populate_from_cart_item(cart_item, request)
