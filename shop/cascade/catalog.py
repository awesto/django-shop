# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ValidationError
from django.template import Template
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopCatalogPlugin(ShopPluginBase):
    name = _("Catalog List Views")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)

    def get_render_template(self, context, instance, placeholder):
        return select_template([
            '{}/catalog/product-list.html'.format(shop_settings.APP_LABEL),
            'shop/catalog/product-list.html',
        ])

plugin_pool.register_plugin(ShopCatalogPlugin)
