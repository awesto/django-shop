# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.encoding import python_2_unicode_compatible
from djangocms_text_ckeditor.fields import HTMLField
from parler.managers import TranslatableManager, TranslatableQuerySet
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.fields import TranslatedField
from shop.money.fields import MoneyField
from shop.models.product import BaseProduct
from myshop.models.properties import Manufacturer, ProductPage, ProductImage


class ProductManager(TranslatableManager):
    queryset_class = TranslatableQuerySet


@python_2_unicode_compatible
class SmartCard(TranslatableModel, BaseProduct):
    # common product fields
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"))
    unit_price = MoneyField(_("Unit price"), decimal_places=3,
        help_text=_("Net price for this product"))
    description = TranslatedField()

    # product properties
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_("Manufacturer"))
    CARD_TYPE = (2 * ('{}{}'.format(s, t),)
                 for t in ('SD', 'SDXC', 'SDHC',) for s in ('', 'micro '))
    card_type = models.CharField(_("Card Type"), choices=CARD_TYPE, max_length='15')
    product_code = models.CharField(_("Product code"), max_length=255, unique=True)
    storage = models.PositiveIntegerField(_("Storage Capacity"),
        help_text=_("Storage capacity in GB"))

    # controlling the catalog
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
    cms_pages = models.ManyToManyField('cms.Page', through=ProductPage, null=True,
        help_text=_("Choose list view this product shall appear on."))
    images = models.ManyToManyField('filer.Image', through=ProductImage, null=True)

    class Meta:
        verbose_name = _("Smart Card")
        verbose_name_plural = _("Smart Cards")
        ordering = ('order',)

    objects = ProductManager()

    def __str__(self):
        return self.name

    @property
    def product_name(self):
        return self.name

    @property
    def product_code(self):
        return self.slug

    @property
    def sample_image(self):
        return self.images.first()

    def get_price(self, request):
        return self.unit_price

    def get_absolute_url(self):
        # sorting by highest level, so that the canonical URL
        # associates with the most generic category
        cms_page = self.cms_pages.order_by('depth').last()
        if cms_page is None:
            return urljoin('category-not-assigned', self.slug)
        return urljoin(cms_page.get_absolute_url(), self.slug)


class SmartCardTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(SmartCard, related_name='translations',
        null=True)
    description = HTMLField(verbose_name=_("Description"),
        help_text=_("Description for the list view of products."))

    class Meta:
        unique_together = [('language_code', 'master')]
