# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap
from django.conf import settings

if settings.SHOP_TUTORIAL in ('commodity', 'i18n_commodity'):
    from shop.models.defaults.commodity import Commodity as Product
elif settings.SHOP_TUTORIAL == 'smartcard':
    from myshop.models.smartcard import SmartCard as Product
elif settings.SHOP_TUTORIAL == 'i18n_smartcard':
    from myshop.models.i18n_smartcard import SmartCard as Product
elif settings.SHOP_TUTORIAL == 'polymorphic':
    from myshop.models.polymorphic.product import Product


class ProductSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    i18n = settings.USE_I18N

    def items(self):
        return Product.objects.filter(active=True)
