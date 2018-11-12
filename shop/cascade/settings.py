# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from cmsplugin_cascade.bootstrap4.mixins import BootstrapUtilities


CASCADE_PLUGINS = getattr(settings, 'SHOP_CASCADE_PLUGINS',
    ('auth', 'breadcrumb', 'catalog', 'cart', 'checkout', 'extensions', 'order', 'processbar', 'search',))


def set_defaults(config):
    config.setdefault('plugins_with_extra_mixins', {})
    config['plugins_with_extra_mixins'].setdefault('ShopReorderButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopCancelOrderButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
