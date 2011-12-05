# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from shop.models.defaults.bases import BaseProduct
from shop.models.defaults.managers import (
    ProductManager,
    ProductStatisticsManager,
)


class Product(BaseProduct):
    objects = ProductManager()
    statistics = ProductStatisticsManager()

    class Meta(object):
        abstract = False
        app_label = 'shop'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
