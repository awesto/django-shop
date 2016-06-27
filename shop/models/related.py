# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum
from six import with_metaclass
from django.db import models
from django.utils.translation import ugettext_lazy
from filer.fields import image
from cms.models.pagemodel import Page
from .product import BaseProduct
from shop import deferred


class ChoiceEnum(Enum):
    """
    Utility class to handle choices in Django model fields
    """
    @classmethod
    def choices(cls):
        values = [p.value for p in cls.__members__.values()]
        if len(values) > len(set(values)):
            msg = "Duplicate values found in {}".format(cls.__class__.__name__)
            raise ValueError(msg)
        choices = [(prop.value, ugettext_lazy('.'.join((cls.__name__, attr))))
                   for attr, prop in cls.__members__.items()]
        return choices


class BaseProductPage(with_metaclass(deferred.ForeignKeyBuilder, models.Model)):
    """
    ManyToMany relation from the polymorphic Product to the CMS Page.
    This in practice is the category.
    """
    page = models.ForeignKey(Page)
    product = deferred.ForeignKey(BaseProduct)

    class Meta:
        abstract = True
        unique_together = ('page', 'product',)
        verbose_name = ugettext_lazy("Category")
        verbose_name_plural = ugettext_lazy("Categories")

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
        verbose_name = ugettext_lazy("Product Image")
        verbose_name_plural = ugettext_lazy("Product Images")
        ordering = ('order',)

ProductImageModel = deferred.MaterializedModel(BaseProductImage)
