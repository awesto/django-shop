# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopCatalogPlugin(ShopPluginBase):
    name = _("Catalog List View")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    cache = False

    def get_render_template(self, context, instance, placeholder):
        return select_template([
            '{}/catalog/product-list.html'.format(shop_settings.APP_LABEL),
            'shop/catalog/product-list.html',
        ])

plugin_pool.register_plugin(ShopCatalogPlugin)


class ShopAddToCartPlugin(ShopPluginBase):
    name = _("Add Product to Cart")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    def get_render_template(self, context, instance, placeholder):
        return select_template([
            '{}/catalog/product-add2cart.html'.format(shop_settings.APP_LABEL),
            'shop/catalog/product-add2cart.html',
        ])

plugin_pool.register_plugin(ShopAddToCartPlugin)
