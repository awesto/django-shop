# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap
from shop.models.product import ProductModel


class ProductsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    i18n = True

    def items(self):
        return ProductModel.objects.all()
