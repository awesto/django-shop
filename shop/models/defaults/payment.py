# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from shop.models_bases import BasePaymentBackend


class PaymentBackend(BasePaymentBackend):

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Payment backend')
        verbose_name_plural = _('Payment backends')
