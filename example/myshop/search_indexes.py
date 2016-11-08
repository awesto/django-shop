# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from haystack import indexes
from shop.search.indexes import ProductIndex as ProductIndexBase


if settings.SHOP_TUTORIAL == 'commodity' or settings.SHOP_TUTORIAL == 'i18n_commodity':
    from shop.models.defaults.commodity import Commodity
elif settings.SHOP_TUTORIAL == 'smartcard':
    from myshop.models.smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from myshop.models.i18n_smartcard import SmartCard
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from myshop.models.polymorphic.smartcard import SmartCard
    from myshop.models.polymorphic.smartphone import SmartPhoneModel


class ProductIndex(ProductIndexBase):
    catalog_media = indexes.CharField(stored=True, indexed=False, null=True)
    search_media = indexes.CharField(stored=True, indexed=False, null=True)
    caption = indexes.CharField(stored=True, indexed=False, null=True, model_attr='caption')

    def prepare_catalog_media(self, product):
        return self.render_html('catalog', product, 'media')

    def prepare_search_media(self, product):
        return self.render_html('search', product, 'media')


myshop_search_index_classes = []

if settings.SHOP_TUTORIAL in ('commodity', 'i18n_commodity'):
    class CommodityIndex(ProductIndex, indexes.Indexable):
        def get_model(self):
            return Commodity

        def Xprepare_text(self, product):
            output = super(CommodityIndex, self).prepare_text(product)
            return output
    myshop_search_index_classes.append(CommodityIndex)


if settings.SHOP_TUTORIAL in ('smartcard', 'i18n_smartcard', 'polymorphic',):
    class SmartCardIndex(ProductIndex, indexes.Indexable):
        def get_model(self):
            return SmartCard
    myshop_search_index_classes.append(SmartCardIndex)


if settings.SHOP_TUTORIAL in ('polymorphic',):
    class SmartPhoneIndex(ProductIndex, indexes.Indexable):
        def get_model(self):
            return SmartPhoneModel
    myshop_search_index_classes.append(SmartPhoneIndex)
