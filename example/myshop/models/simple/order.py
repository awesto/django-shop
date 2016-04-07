# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models.order import BaseOrderItem


class OrderItem(BaseOrderItem):
    quantity = models.IntegerField(_("Ordered quantity"))

    def populate_from_cart_item(self, cart_item, request):
        self.product_code = cart_item.product.product_code
        super(OrderItem, self).populate_from_cart_item(cart_item, request)
