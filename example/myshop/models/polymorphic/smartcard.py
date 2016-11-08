# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from shop.money.fields import MoneyField
from parler.models import TranslatedFields
from .product import Product


class SmartCard(Product):
    # common product fields
    unit_price = MoneyField(_("Unit price"), decimal_places=3,
                            help_text=_("Net price for this product"))

    # product properties
    CARD_TYPE = (2 * ('{}{}'.format(s, t),)
                 for t in ('SD', 'SDXC', 'SDHC', 'SDHC II') for s in ('', 'micro '))
    card_type = models.CharField(_("Card Type"), choices=CARD_TYPE, max_length=15)
    SPEED = [(str(s), "{} MB/s".format(s)) for s in (4, 20, 30, 40, 48, 80, 95, 280)]
    speed = models.CharField(_("Transfer Speed"), choices=SPEED, max_length=8)
    product_code = models.CharField(_("Product code"), max_length=255, unique=True)
    storage = models.PositiveIntegerField(_("Storage Capacity"),
                                          help_text=_("Storage capacity in GB"))
    multilingual = TranslatedFields(
        description=HTMLField(verbose_name=_("Description"),
                              configuration='CKEDITOR_SETTINGS_DESCRIPTION',
                              help_text=_("Full description used in the catalog's detail view of Smart Cards.")))

    class Meta:
        verbose_name = _("Smart Card")
        verbose_name_plural = _("Smart Cards")

    def get_price(self, request):
        return self.unit_price

    def get_product_variant(self, extra):
        """
        SmartCards do not have flavors, they are the product.
        """
        return self
