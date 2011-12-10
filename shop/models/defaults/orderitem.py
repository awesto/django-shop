# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from shop.models.defaults.bases import BaseOrderItem


class OrderItem(BaseOrderItem):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')
