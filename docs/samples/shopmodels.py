# -*- coding: utf-8 -*-
from shop.models.deferred import ForeignKeyBuilder
ForeignKeyBuilder.app_label = 'myshop'
from shop.models import cart, order, product


class Cart(cart.BaseCart):
    pass


class CartItem(cart.BaseCartItem):
    pass


class Order(order.BaseOrder):
    pass


class OrderItem(order.BaseOrderItem):
    pass


class Product(product.BaseProduct):
    class Meta:
        app_label = 'myshop'
