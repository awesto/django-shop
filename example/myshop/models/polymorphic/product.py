# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.fields import TranslatedField
from parler.managers import TranslatableManager, TranslatableQuerySet
from polymorphic.query import PolymorphicQuerySet
from shop.models.product import BaseProductManager, BaseProduct
from shop.models.defaults.mapping import ProductPage, ProductImage
from myshop.models.properties import Manufacturer


class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class ProductManager(BaseProductManager, TranslatableManager):
    queryset_class = ProductQuerySet


@python_2_unicode_compatible
class Product(BaseProduct, TranslatableModel):
    product_name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    slug = models.SlugField(verbose_name=_("Slug"), unique=True)
    description = TranslatedField()

    # common product properties
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_("Manufacturer"))

    # controlling the catalog
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
    cms_pages = models.ManyToManyField('cms.Page', through=ProductPage,
        help_text=_("Choose list view this product shall appear on."))
    images = models.ManyToManyField('filer.Image', through=ProductImage)

    class Meta:
        ordering = ('order',)

    objects = ProductManager()

    # filter expression used to lookup for a product item using the Select2 widget
    lookup_fields = ('product_name__icontains',)

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        # sorting by highest level, so that the canonical URL associates with the most generic category
        cms_page = self.cms_pages.order_by('depth').last()
        if cms_page is None:
            return urljoin('category-not-assigned', self.slug)
        return urljoin(cms_page.get_absolute_url(), self.slug)

    @property
    def sample_image(self):
        return self.images.first()

    def get_product_variant(self, extra):
        """
        Get a variant of the product or itself, if the product has no flavors.
        Raises `Product.objects.DoesNotExists` if there is no variant for the given `extra`.
        """
        msg = "Method get_product_variant(extra) must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))


class ProductTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Product, related_name='translations', null=True)
    description = HTMLField(verbose_name=_("Description"),
                            help_text=_("Description for the list view of products."))

    class Meta:
        unique_together = [('language_code', 'master')]
