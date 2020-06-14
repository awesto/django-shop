from django.db import models
from django.utils.translation import gettext_lazy as _

from filer.fields import image

from cms.models.pagemodel import Page

from shop import deferred
from shop.models.product import BaseProduct


class BaseProductPage(models.Model, metaclass=deferred.ForeignKeyBuilder):
    """
    ManyToMany relation from the polymorphic Product to the CMS Page.
    This in practice is the category.
    """
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )

    product = deferred.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        unique_together = ['page', 'product']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

ProductPageModel = deferred.MaterializedModel(BaseProductPage)


class BaseProductImage(models.Model, metaclass=deferred.ForeignKeyBuilder):
    """
    ManyToMany relation from the polymorphic Product to a set of images.
    """
    image = image.FilerImageField(on_delete=models.CASCADE)

    product = deferred.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
    )

    order = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['order']

ProductImageModel = deferred.MaterializedModel(BaseProductImage)
