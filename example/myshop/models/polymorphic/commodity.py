# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models.fields import PlaceholderField
from parler.managers import TranslatableManager
from shop.money.fields import MoneyField
from .product import Product


class Commodity(Product):
    """
    This Commodity model inherits from polymorphic Product, and therefore has to be redefined.
    """

    # common product fields
    unit_price = MoneyField(_("Unit price"), decimal_places=3,
                            help_text=_("Net price for this product"))
    product_code = models.CharField(_("Product code"), max_length=255, unique=True)

    # controlling the catalog
    placeholder = PlaceholderField("Commodity Details")
    show_breadcrumb = True  # hard coded to always show the product's breadcrumb

    default_manager = TranslatableManager()

    class Meta:
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    def get_price(self, request):
        return self.unit_price
