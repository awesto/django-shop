# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
import reversion
from .shopmodels import Product


@python_2_unicode_compatible
class Commodity(Product):
    cms_pages = models.ManyToManyField('cms.Page', blank=True,
        help_text=_("Choose list view this commodity shall appear on."))

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    def __str__(self):
        return self.name

reversion.register(Commodity, follow=['product_ptr'])
