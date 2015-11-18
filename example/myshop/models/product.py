# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from filer.fields import image
from filer.models import Image
from cms.models.fields import PlaceholderField
from cms.models.pagemodel import Page
from djangocms_text_ckeditor.fields import HTMLField
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.fields import TranslatedField
from parler.managers import TranslatableManager, TranslatableQuerySet
from polymorphic.query import PolymorphicQuerySet
import reversion
from shop.models.product import BaseProductManager, BaseProduct


class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class ProductManager(BaseProductManager, TranslatableManager):
    queryset_class = ProductQuerySet

    def select_lookup(self, term):
        query = models.Q(name__icontains=term) | models.Q(slug__icontains=term)
        return self.get_queryset().filter(query)


class Product(TranslatableModel, BaseProduct):
    order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"))
    description = TranslatedField()
    cms_pages = models.ManyToManyField(Page, through='ProductPage', null=True,
        help_text=_("Choose list view this product shall appear on."))
    images = models.ManyToManyField(Image, through='ProductImage', null=True)
    placeholder = PlaceholderField("Product Detail",
        verbose_name=_("Additional description for this product."))

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        ordering = ('order',)

    objects = ProductManager()

    # filter expression used to search for a product item using the Select2 widget
    search_fields = ('identifier__istartswith', 'translations__name__istartswith',)

    def get_absolute_url(self):
        # sorting by highest level, so that the canonical URL associates with the most generic category
        cms_page = self.cms_pages.order_by('depth').last()
        if cms_page is None:
            return urljoin('category-not-assigned', self.slug)
        return urljoin(cms_page.get_absolute_url(), self.slug)

    @property
    def product_name(self):
        return self.name

    @property
    def sample_image(self):
        return self.images.first()

    def get_product_markedness(self, extra):
        """
        Get the markedness of a product.
        Raises `Product.objects.DoesNotExists` if there is no markedness for the given `extra`.
        """
        msg = "Method get_product_markedness(extra) must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

reversion.register(Product, adapter_cls=type(str('ProductVersionAdapter'), (reversion.VersionAdapter,),
                                             {'format': 'shop'}))


class ProductTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Product, related_name='translations', null=True)
    description = HTMLField(verbose_name=_("Description"),
                            help_text=_("Description for the list view of products."))

    class Meta:
        unique_together = [('language_code', 'master')]
        app_label = settings.SHOP_APP_LABEL


class ProductPage(models.Model):
    """
    Explicit ManyToMany relation from CMS Page to Product. This is in practice is the category.
    """
    page = models.ForeignKey(Page)
    product = models.ForeignKey(Product)

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class ProductImage(models.Model):
    image = image.FilerImageField()
    product = models.ForeignKey(Product)
    order = models.SmallIntegerField(default=0, blank=False, null=False)

    class Meta:
        app_label = settings.SHOP_APP_LABEL
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ('order',)


@python_2_unicode_compatible
class Manufacturer(models.Model):
    name = models.CharField(_("Name"), max_length=50)

    def __str__(self):
        return self.name
