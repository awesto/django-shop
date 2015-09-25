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
    cost = models.CharField(choices=(('per_piece', _("per piece")), ('per_meter', _("per meter")),),
        max_length=12, default='per_piece', verbose_name=_("Cost"))
    cms_pages = models.ManyToManyField('cms.Page', blank=True,
        help_text=_("Choose list view this commodity shall appear on."))

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    def __str__(self):
        return self.name

    def is_in_cart(self, cart, extra, watched=False):
        if not watched and self.cost == 'per_meter':
            return None
        return super(Commodity, self).is_in_cart(cart, extra, watched)

reversion.register(Commodity, follow=['product_ptr'])
