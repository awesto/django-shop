# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from shop.models.defaults.bases import BaseOrderExtraInfo, BaseExtraOrderPriceField, \
                                       BaseExtraOrderItemPriceField, BaseOrderPayment


class OrderExtraInfo(BaseOrderExtraInfo):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Order extra info')
        verbose_name_plural = _('Order extra info')


class ExtraOrderPriceField(BaseExtraOrderPriceField):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Extra order price field')
        verbose_name_plural = _('Extra order price fields')


class ExtraOrderItemPriceField(BaseExtraOrderItemPriceField):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Extra order item price field')
        verbose_name_plural = _('Extra order item price fields')


class OrderPayment(BaseOrderPayment):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Order payment')
        verbose_name_plural = _('Order payments')



