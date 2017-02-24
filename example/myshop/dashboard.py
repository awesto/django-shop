# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.views import dashboard


class ProductsDashboard(dashboard.ProductsDashboard):
    list_display = ['media', 'product_name', 'caption', 'price']
    list_display_links = ['product_name']

dashboard.router.register('products', ProductsDashboard, base_name='product')
