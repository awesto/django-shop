# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from cms.models.fields import PlaceholderField
from filer.fields import image
from djangocms_text_ckeditor.fields import HTMLField
from polymorphic.query import PolymorphicQuerySet
from shop.models.product import BaseProduct, BaseProductManager
from shop.models.defaults.mapping import ProductPage
from shop.money.fields import MoneyField


if settings.USE_I18N:
    if 'parler' not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("Requires `django-parler`, if configured as multilingual project")

    from parler.managers import TranslatableManager, TranslatableQuerySet
    from parler.models import TranslatableModel, TranslatedFieldsModel
    from parler.fields import TranslatedField


    class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
        pass


    class ProductManager(BaseProductManager, TranslatableManager):
        queryset_class = ProductQuerySet


    @python_2_unicode_compatible
    class Commodity(BaseProduct, TranslatableModel):
        """
        Generic Product Commodity to be used whenever the merchant does not require product specific
        attributes and just required a placeholder field to add arbitrary data.
        """
        # common product fields
        product_code = models.CharField(_("Product code"), max_length=255, unique=True)
        unit_price = MoneyField(_("Unit price"), decimal_places=3,
                                help_text=_("Net price for this product"))

        # controlling the catalog
        order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
        cms_pages = models.ManyToManyField('cms.Page', through=ProductPage,
            help_text=_("Choose list view this product shall appear on."))
        sample_image = image.FilerImageField(blank=True)
        placeholder = PlaceholderField("Commodity Details")

        # translatable fields for the catalog's list- and detail views
        translated_product_name = TranslatedField()
        slug = TranslatedField()
        description = TranslatedField()

        # filter expression used to search for a product item using the Select2 widget
        lookup_fields = ('product_code__startswith', 'product_name__icontains',)

        objects = ProductManager()

        class Meta:
            app_label = settings.SHOP_APP_LABEL
            ordering = ('order',)
            verbose_name = _("Commodity")
            verbose_name_plural = _("Commodities")

        def __str__(self):
            return self.product_code

        def product_name(self):
            return self.translated_product_name

        def get_price(self, request):
            return self.unit_price


    class CommodityTranslation(TranslatedFieldsModel):
        master = models.ForeignKey(Commodity, related_name='translations', null=True)
        translated_product_name = models.CharField(max_length=255, verbose_name=_("Product Name"))
        slug = models.SlugField(verbose_name=_("Slug"))
        description = HTMLField(verbose_name=_("Description"), blank=True, null=True,
                                help_text=_("Description for the list view of products."))

        class Meta:
            app_label = settings.SHOP_APP_LABEL
            unique_together = [('language_code', 'master')]

else:

    @python_2_unicode_compatible
    class Commodity(BaseProduct):
        """
        Generic Product Commodity to be used whenever the merchant does not require product specific
        attributes and just required a placeholder field to add arbitrary data.
        """
        # common product fields
        product_name = models.CharField(max_length=255, verbose_name=_("Product Name"))
        product_code = models.CharField(_("Product code"), max_length=255, unique=True)
        unit_price = MoneyField(_("Unit price"), decimal_places=3,
                                help_text=_("Net price for this product"))

        # controlling the catalog
        order = models.PositiveIntegerField(verbose_name=_("Sort by"), db_index=True)
        cms_pages = models.ManyToManyField('cms.Page', through=ProductPage,
            help_text=_("Choose list view this product shall appear on."))
        sample_image = image.FilerImageField()
        placeholder = PlaceholderField("Commodity Details")

        # common fields for the catalog's list- and detail views
        slug = models.SlugField(verbose_name=_("Slug"))
        description = HTMLField(verbose_name=_("Description"),
             help_text=_("Description for the list view of products."))

        # filter expression used to search for a product item using the Select2 widget
        lookup_fields = ('product_code__startswith', 'product_name__icontains',)

        objects = BaseProductManager()

        class Meta:
            app_label = settings.SHOP_APP_LABEL
            ordering = ('order',)
            verbose_name = _("Commodity")
            verbose_name_plural = _("Commodities")

        def __str__(self):
            return self.product_code

        def get_price(self, request):
            return self.unit_price
