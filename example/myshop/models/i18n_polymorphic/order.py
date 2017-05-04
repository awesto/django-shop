# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.models import order
from shop.models.cart import CartItemModel


class OrderItem(order.BaseOrderItem):
    quantity = models.IntegerField(_("Ordered quantity"))
    canceled = models.BooleanField(_("Item canceled "), default=False)

    def populate_from_cart_item(self, cart_item, request):
        super(OrderItem, self).populate_from_cart_item(cart_item, request)
        # the product's unit_price must be fetched from the product's variant
        try:
            variant = cart_item.product.get_product_variant(product_code=cart_item.product_code)
            self._unit_price = Decimal(variant.unit_price)
        except (KeyError, ObjectDoesNotExist) as e:
            raise CartItemModel.DoesNotExist(e)
