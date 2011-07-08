# -*- coding: utf-8 -*-
from shop.models.defaults.bases import BaseCart, BaseCartItem


class Cart(BaseCart):
    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')


class CartItem(BaseCartItem):
    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')
