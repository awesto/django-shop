# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from filer.fields.image import FilerImageField

from parler.models import TranslatableModelMixin, TranslatedFieldsModel
from parler.fields import TranslatedField
from parler.managers import TranslatableManager, TranslatableQuerySet

from polymorphic.query import PolymorphicQuerySet

from shop.models.product import BaseProductManager, BaseProduct
from ..manufacturer import Manufacturer


class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class ProductManager(BaseProductManager, TranslatableManager):
    queryset_class = ProductQuerySet

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db)
        return qs.prefetch_related('translations')


@python_2_unicode_compatible
class Product(TranslatableModelMixin, BaseProduct):
    """
    Base class to describe a polymorphic product. Here we declare common fields available in all of
    our different product types. These common fields are also used to build up the view displaying
    a list of all products.
    """
    product_name = models.CharField(
        _("Product Name"),
        max_length=255,
    )

    slug = models.SlugField(
        _("Slug"),
        unique=True,
    )

    caption = TranslatedField()

    # common product properties
    manufacturer = models.ForeignKey(
        Manufacturer,
        verbose_name=_("Manufacturer"),
    )

    sample_image = FilerImageField(
        null=True,
        blank=True,
        related_name='sample_image',
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    objects = ProductManager()

    # filter expression used to lookup for a product item using the Select2 widget
    lookup_fields = ('product_name__icontains',)

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        """
        Return the absolute URL of a product
        """
        return '/bah/blah'


class ProductTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(
        Product,
        related_name='translations',
        null=True,
    )

    caption = models.TextField(
        verbose_name=_("Caption"),
        blank=True,
        null=True,
        help_text=_("Caption used in the catalog's list view of products."),
    )

    class Meta:
        unique_together = [('language_code', 'master')]
