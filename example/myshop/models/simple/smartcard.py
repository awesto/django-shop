# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.encoding import python_2_unicode_compatible
from djangocms_text_ckeditor.fields import HTMLField
from shop.money.fields import MoneyField
from shop.models.product import BaseProduct, BaseProductManager
from shop.models.defaults.mapping import ProductPage, ProductImage
from myshop.models.properties import Manufacturer


@python_2_unicode_compatible
class SmartCard(BaseProduct):
    # common product fields
    product_name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    slug = models.SlugField(verbose_name=_("Slug"))
    unit_price = MoneyField(_("Unit price"), decimal_places=3,
        help_text=_("Net price for this product"))
    description = HTMLField(verbose_name=_("Description"),
                            help_text=_("Description for the list view of products."))

    # product properties
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_("Manufacturer"))
    CARD_TYPE = (2 * ('{}{}'.format(s, t),)
                 for t in ('SD', 'SDXC', 'SDHC', 'SDHC II') for s in ('', 'micro '))
    card_type = models.CharField(_("Card Type"), choices=CARD_TYPE, max_length=15)
    SPEED = ((str(s), "{} MB/s".format(s)) for s in (4, 20, 30, 40, 48, 80, 95, 280))
    speed = models.CharField(_("Transfer Speed"), choices=SPEED, max_length=8)
    product_code = models.CharField(_("Product code"), max_length=255, unique=True)
    storage = models.PositiveIntegerField(_("Storage Capacity"),
        help_text=_("Storage capacity in GB"))

    # controlling the catalog
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
    cms_pages = models.ManyToManyField('cms.Page', through=ProductPage,
        help_text=_("Choose list view this product shall appear on."))
    images = models.ManyToManyField('filer.Image', through=ProductImage)

    objects = BaseProductManager()

    # filter expression used to search for a product item using the Select2 widget
    lookup_fields = ('product_code__startswith', 'product_name__icontains',)

    class Meta:
        verbose_name = _("Smart Card")
        verbose_name_plural = _("Smart Cards")
        ordering = ('order',)

    def __str__(self):
        return self.product_name

    @property
    def sample_image(self):
        return self.images.first()

    def get_price(self, request):
        return self.unit_price

    def get_absolute_url(self):
        # sorting by highest level, so that the canonical URL associates with the
        # most generic category
        cms_page = self.cms_pages.order_by('depth').last()
        if cms_page is None:
            return urljoin('category-not-assigned', self.slug)
        return urljoin(cms_page.get_absolute_url(), self.slug)
