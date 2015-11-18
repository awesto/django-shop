# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
import reversion
from shop.money.fields import MoneyField
from .product import Product, Manufacturer


@python_2_unicode_compatible
class SmartCard(Product):
    """
    A generic smart phone model, which must be concretized by a model `SmartPhone` - see below.
    """
    CARD_TYPE = (2 * ('{}{}'.format(s, t),) for t in ('SD', 'SDXC', 'SDHC',) for s in ('', 'micro '))
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_("Manufacturer"))
    cart_type = models.CharField(_("Card Type"), choices=CARD_TYPE, max_length='15')
    product_code = models.CharField(_("Product code"), max_length=255, unique=True)
    unit_price = MoneyField(_("Unit price"), decimal_places=3,
        help_text=_("Net price for this product"))
    storage = models.PositiveIntegerField(_("Storage Capacity"),
        help_text=_("Storage capacity in GB"))

    def get_price(self, request):
        return self.unit_price

    class Meta:
        verbose_name = _("Smart Card")
        verbose_name_plural = _("Smart Card")

    def __str__(self):
        return self.name

reversion.register(SmartCard, follow=['product_ptr'])
