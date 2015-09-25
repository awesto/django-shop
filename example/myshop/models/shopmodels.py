# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from filer.fields import image
from filer.models import Image
from cms.models.fields import PlaceholderField
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.fields import TranslatedField
from parler.managers import TranslatableManager, TranslatableQuerySet
from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet
import reversion
from shop.models.product import BaseProduct
from shop.money.fields import MoneyField


class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class ProductManager(PolymorphicManager, TranslatableManager):
    queryset_class = ProductQuerySet


class Product(TranslatableModel, BaseProduct):
    identifier = models.CharField(max_length=255, verbose_name=_("Product code"))
    unit_price = MoneyField(verbose_name=_("Unit price"), decimal_places=3,
        help_text=_("Net price for this product"))  # TODO: , min_value=0
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
    name = TranslatedField()
    slug = TranslatedField()
    description = TranslatedField()
    images = models.ManyToManyField(Image, through='ProductImage', null=True)
    placeholder = PlaceholderField('Textile Detail',
        verbose_name=_("Details for this textile"))
    availability = models.SmallIntegerField(default=1,
        choices=((0, _("Sold out")), (1, _("1 day")), (4, _("4 days")), (7, _("7 days")),),
        verbose_name=_("Availability"),
        help_text=_("Ready for shipping in days"))

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        ordering = ('order',)

    objects = ProductManager()

    # filter expression used to search for a product item using the Select2 widget
    search_fields = ('identifier__istartswith', 'translations__name__istartswith',)

    def get_price(self, request):
        gross_price = self.unit_price * (1 + settings.SHOP_VALUE_ADDED_TAX / 100)
        return gross_price

    def get_absolute_url(self):
        # sorting by highest level, so that the canonical URL associates with the most generic category
        cms_page = self.cms_pages.order_by('depth').last()
        if cms_page is None:
            return urljoin('category-not-assigned', self.slug)
        return urljoin(cms_page.get_absolute_url(), self.slug)

    @property
    def sample_image(self):
        return self.images.first()

reversion.register(Product, adapter_cls=type(str('ProductVersionAdapter'), (reversion.VersionAdapter,),
                                             {'format': 'shop'}))


class ProductTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Product, related_name='translations', null=True)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"))
    description = HTMLField(verbose_name=_("Description"),
                            help_text=_("Description for the list view of products."))

    class Meta:
        unique_together = [('language_code', 'master'), ('language_code', 'slug')]
        db_table = 'stofferia_product_translation'
        app_label = settings.SHOP_APP_LABEL


class ProductImage(models.Model):
    image = image.FilerImageField()
    product = models.ForeignKey(Product)
    order = models.SmallIntegerField(default=0, blank=False, null=False)

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ('order',)
