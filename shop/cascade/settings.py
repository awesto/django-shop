# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig


CASCADE_PLUGINS = getattr(settings, 'SHOP_CASCADE_PLUGINS',
    ('auth', 'breadcrumb', 'catalog', 'cart', 'checkout', 'extensions', 'order', 'processbar', 'search',))


def set_defaults(config):
    config.setdefault('plugins_with_extra_fields', {})
    config['plugins_with_extra_fields'].setdefault('ShopReorderButtonPlugin', PluginExtraFieldsConfig(
        inline_styles={
            'extra_fields:Margins': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
            'extra_units:Margins': 'px,em'
        },
    ))
    config['plugins_with_extra_fields'].setdefault('ShopCancelOrderButtonPlugin', PluginExtraFieldsConfig(
        inline_styles={
            'extra_fields:Margins': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
            'extra_units:Margins': 'px,em'
        },
    ))
