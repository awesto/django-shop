# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from shop.models_bases import BaseShippingBackend


class ShippingBackend(BaseShippingBackend):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Shipping backend')
        verbose_name_plural = _('Shipping backends')
