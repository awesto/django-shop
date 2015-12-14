# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shop.search.indexes import ProductIndex as ProductIndexBase
from haystack import indexes


class ProductIndex(ProductIndexBase):
    description = indexes.CharField(stored=True, indexed=False, null=True)
    media = indexes.CharField(stored=True, indexed=False, null=True)

    def prepare_description(self, product):
        return product.description

    def prepare_media(self, product):
        return self.render_html(product, 'media')
