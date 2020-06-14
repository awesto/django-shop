"""
In django-SHOP, a Commodity product-model is considered a very basic product without any attributes,
which can be used on a generic CMS page to describe anything.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from cms.models.fields import PlaceholderField
from filer.fields import image
from djangocms_text_ckeditor.fields import HTMLField
from polymorphic.query import PolymorphicQuerySet
from shop.conf import app_settings
from shop.models.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin, AvailableProductMixin
from shop.models.defaults.mapping import ProductPage
from shop.money.fields import MoneyField


class CommodityMixin(AvailableProductMixin):
    """
    Common methods used by both default Commodity models.
    """
    def get_price(self, request):
        return self.unit_price


if settings.USE_I18N:
    assert 'parler' in settings.INSTALLED_APPS, "Requires `django-parler`, if configured as multilingual project"
    from parler.managers import TranslatableManager, TranslatableQuerySet
    from parler.models import TranslatableModelMixin, TranslatedFieldsModel
    from parler.fields import TranslatedField


    class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
        pass


    class ProductManager(BaseProductManager, TranslatableManager):
        queryset_class = ProductQuerySet


    class Commodity(CMSPageReferenceMixin, TranslatableModelMixin, CommodityMixin, BaseProduct):
        """
        Generic Product Commodity to be used whenever the merchant does not require product specific
        attributes and just required a placeholder field to add arbitrary data.
        """
        # common product fields
        product_code = models.CharField(
            _("Product code"),
            max_length=255,
            unique=True,
        )

        unit_price = MoneyField(
            _("Unit price"),
            decimal_places=3,
            help_text=_("Net price for this product"),
        )

        # controlling the catalog
        order = models.PositiveIntegerField(
            verbose_name=_("Sort by"),
            db_index=True,
        )

        cms_pages = models.ManyToManyField(
            'cms.Page',
            through=ProductPage,
            help_text=_("Choose list view this product shall appear on."),
        )

        sample_image = image.FilerImageField(
            verbose_name=_("Sample Image"),
            blank=True,
            null=True,
            default=None,
            on_delete=models.SET_DEFAULT,
            help_text=_("Sample image used in the catalog's list view."),
        )

        show_breadcrumb = models.BooleanField(
            _("Show Breadcrumb"),
            default=True,
            help_text=_("Shall the detail page show the product's breadcrumb."),
        )

        placeholder = PlaceholderField("Commodity Details")

        quantity = models.PositiveIntegerField(
            _("Quantity"),
            default=0,
            validators=[MinValueValidator(0)],
            help_text=_("Available quantity in stock")
        )

        # translatable fields for the catalog's list- and detail views
        product_name = TranslatedField()
        slug = TranslatedField()
        caption = TranslatedField()

        # filter expression used to search for a product item using the Select2 widget
        lookup_fields = ['product_code__startswith', 'product_name__icontains']

        objects = ProductManager()

        class Meta:
            app_label = app_settings.APP_LABEL
            ordering = ['order']
            verbose_name = _("Commodity")
            verbose_name_plural = _("Commodities")

        def __str__(self):
            return self.product_code


    class CommodityTranslation(TranslatedFieldsModel):
        master = models.ForeignKey(
            Commodity,
            related_name='translations',
            on_delete=models.CASCADE,
            null=True,
        )

        product_name = models.CharField(
            max_length=255,
            verbose_name=_("Product Name"),
        )

        slug = models.SlugField(verbose_name=_("Slug"))

        caption = HTMLField(
            verbose_name=_("Caption"),
            blank=True,
            null=True,
            help_text=_("Short description for the catalog list view."),
        )

        class Meta:
            app_label = app_settings.APP_LABEL
            unique_together = [('language_code', 'master')]

else:

    class Commodity(CMSPageReferenceMixin, CommodityMixin, BaseProduct):
        """
        Generic Product Commodity to be used whenever the merchant does not require product specific
        attributes and just required a placeholder field to add arbitrary data.
        """
        # common product fields
        product_name = models.CharField(
            max_length=255,
            verbose_name=_("Product Name"),
        )

        product_code = models.CharField(
            _("Product code"),
            max_length=255,
            unique=True,
        )

        unit_price = MoneyField(
            _("Unit price"),
            decimal_places=3,
            help_text=_("Net price for this product"),
        )

        # controlling the catalog
        order = models.PositiveIntegerField(
            verbose_name=_("Sort by"),
            db_index=True,
        )

        cms_pages = models.ManyToManyField(
            'cms.Page',
            through=ProductPage,
            help_text=_("Choose list view this product shall appear on."),
        )

        sample_image = image.FilerImageField(
            verbose_name=_("Sample Image"),
            blank=True,
            null=True,
            default=None,
            on_delete=models.SET_DEFAULT,
            help_text=_("Sample image used in the catalog's list view."),
        )

        show_breadcrumb = models.BooleanField(
            _("Show Breadcrumb"),
            default=True,
            help_text=_("Shall the detail page show the product's breadcrumb."),
        )

        placeholder = PlaceholderField("Commodity Details")

        quantity = models.PositiveIntegerField(
            _("Quantity"),
            default=0,
            validators=[MinValueValidator(0)],
            help_text=_("Available quantity in stock")
        )

        # common fields for the catalog's list- and detail views
        slug = models.SlugField(verbose_name=_("Slug"))

        caption = HTMLField(
            verbose_name=_("Caption"),
            blank=True,
            null=True,
            help_text=_("Short description for the catalog list view."),
        )

        # filter expression used to search for a product item using the Select2 widget
        lookup_fields = ['product_code__startswith', 'product_name__icontains']

        objects = BaseProductManager()

        class Meta:
            app_label = app_settings.APP_LABEL
            ordering = ('order',)
            verbose_name = _("Commodity")
            verbose_name_plural = _("Commodities")

        def __str__(self):
            return self.product_code
