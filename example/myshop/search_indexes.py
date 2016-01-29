# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from shop.search.indexes import ProductIndex as ProductIndexBase
from haystack import indexes

if settings.SHOP_TUTORIAL == 'simple':
    from myshop.models.simple.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'i18n':
    from myshop.models.i18n.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from myshop.models.polymorphic.smartcard import SmartCard
    from myshop.models.polymorphic.smartphone import SmartPhoneModel


class ProductIndex(ProductIndexBase):
    catalog_media = indexes.CharField(stored=True, indexed=False, null=True)
    search_media = indexes.CharField(stored=True, indexed=False, null=True)

    def prepare_catalog_media(self, product):
        return self.render_html('catalog', product, 'media')

    def prepare_search_media(self, product):
        return self.render_html('search', product, 'media')


class SmartCardIndex(ProductIndex, indexes.Indexable):
    def get_model(self):
        return SmartCard


if settings.SHOP_TUTORIAL == 'polymorphic':
    class SmartPhoneIndex(ProductIndex, indexes.Indexable):
        def get_model(self):
            return SmartPhoneModel
    myshop_search_index_classes = (SmartCardIndex, SmartPhoneIndex)
else:
    myshop_search_index_classes = (SmartCardIndex,)
