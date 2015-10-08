# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible, force_text
from filer.fields import image
from parler.models import TranslatableModel, TranslatedFields
import reversion
from .shopmodels import Product


@python_2_unicode_compatible
class CommodityProperty(TranslatableModel, models.Model):
    multiple_tags = models.BooleanField(default=False,
        verbose_name=_("Customer can select multiple tags for this property"))
    translations = TranslatedFields(
        property=models.CharField(max_length=255, verbose_name=_("Property"),
            help_text=_("One of some possible properties for commodities.")),
    )

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Commodity Property")
        verbose_name_plural = _("Commodity Properties")

    def __str__(self):
        return force_text(self.property)


@python_2_unicode_compatible
class CommodityTag(TranslatableModel, models.Model):
    property = models.ForeignKey(CommodityProperty)
    translations = TranslatedFields(
        tag=models.CharField(max_length=255, verbose_name=_("Tag"),
            help_text=_("A tag to describe the property of this commodity.")),
        search_indices=models.CharField(max_length=255, verbose_name=_("Search Indices"),
            help_text=_("Search Indices for describing this property tag"), null=True, blank=True)
    )
    image = image.FilerImageField(null=True, blank=True, related_name='tex_tag',
        verbose_name=_("Sample Image"),
        help_text=_("A sample image get an impression of this tag"))

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Commodity Tag")
        verbose_name_plural = _("Commodity Tags")

    def __str__(self):
        return force_text(self.tag)


@python_2_unicode_compatible
class Commodity(Product):
    cms_pages = models.ManyToManyField('cms.Page', blank=True,
        help_text=_("Choose list view this commodity shall appear on."))
    properties = models.ManyToManyField(CommodityTag, blank=True,
        help_text=_("Choose properties for this commodity."))

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    def __str__(self):
        return self.name

reversion.register(Commodity, follow=['product_ptr'])
