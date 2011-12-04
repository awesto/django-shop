# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from shop.models.defaults.bases import BaseCart


class Cart(BaseCart):
    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
