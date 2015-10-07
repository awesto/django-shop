# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.search.indexes import ProductIndex as ProductIndexBase
from myshop.models.commodity import Commodity
from haystack import indexes


class ProductIndex(ProductIndexBase):
    description = indexes.CharField(stored=True, indexed=False, null=True)
    media = indexes.CharField(stored=True, indexed=False, null=True)

    def prepare_description(self, product):
        return product.description

    def prepare_media(self, product):
        return self.render_html(product, 'media')


class CommodityIndex(ProductIndex, indexes.Indexable):
    def get_model(self):
        return Commodity
