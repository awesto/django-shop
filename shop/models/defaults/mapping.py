# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Some models in the merchant's implementation require a many-to-many relation with models from
outside django-SHOP. Therefore these mapping tables must be materialized by the merchant's
implementation.
"""
from shop.models.related import BaseProductPage, BaseProductImage


class ProductPage(BaseProductPage):
    """Materialize many-to-many relation with CMS pages"""


class ProductImage(BaseProductImage):
    """Materialize many-to-many relation with images"""
    class Meta(BaseProductImage.Meta):
        abstract = False
