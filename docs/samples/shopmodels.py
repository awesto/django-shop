# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shop.util.fields import CurrencyField
from shop.models import cart, order, product


class Cart(cart.BaseCart):
    class Meta:
        app_label = 'myshop'


class CartItem(cart.BaseCartItem):
    class Meta:
        app_label = 'myshop'


class Order(order.BaseOrder):
    class Meta:
        app_label = 'myshop'


class OrderItem(order.BaseOrderItem):
    class Meta:
        app_label = 'myshop'


class OrderExtraRow(order.BaseOrderExtraRow):
    class Meta:
        app_label = 'myshop'


class OrderItemExtraRow(order.BaseItemExtraRow):
    class Meta:
        app_label = 'myshop'


class Product(product.BaseProduct):
    class Meta:
        app_label = 'myshop'

    product_code = models.CharField(max_length=255, verbose_name=_("Product code"))
    unit_price = CurrencyField(verbose_name=_("Unit price"))
    active = models.BooleanField(default=False, verbose_name=_("Availability of product"))
