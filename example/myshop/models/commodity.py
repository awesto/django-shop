# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from .shopmodels import Product


@python_2_unicode_compatible
class Commodity(Product):
    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    def __str__(self):
        return self.name
