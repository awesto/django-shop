# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _

from filer.fields import image

from cms.models.pagemodel import Page

from shop import deferred
from shop.models.product import BaseProduct


class BaseProductPage(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    ManyToMany relation from the polymorphic Product to the CMS Page.
    This in practice is the category.
    """
    page = models.ForeignKey(Page)
    product = deferred.ForeignKey(BaseProduct)

    class Meta:
        abstract = True
        unique_together = ['page', 'product']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

ProductPageModel = deferred.MaterializedModel(BaseProductPage)


class BaseProductImage(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    ManyToMany relation from the polymorphic Product to a set of images.
    """
    image = image.FilerImageField()
    product = deferred.ForeignKey(BaseProduct)
    order = models.SmallIntegerField(default=0, blank=False, null=False)

    class Meta:
        abstract = True
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['order']

ProductImageModel = deferred.MaterializedModel(BaseProductImage)
