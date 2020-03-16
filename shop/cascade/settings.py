# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig
from cmsplugin_cascade.bootstrap4.mixins import BootstrapUtilities


CASCADE_PLUGINS = getattr(settings, 'SHOP_CASCADE_PLUGINS',
    ['auth', 'breadcrumb', 'catalog', 'cart', 'checkout', 'extensions', 'order', 'processbar', 'search', 'navbar_shop']
)


def set_defaults(config):
    config.setdefault('plugins_with_extra_mixins', {})
    config.setdefault('plugins_with_extra_render_templates', {})
    config['plugins_with_extra_mixins'].setdefault('ShopReorderButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.margins, BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopCancelOrderButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.margins, BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopProceedButton', BootstrapUtilities(
        BootstrapUtilities.margins, BootstrapUtilities.floats,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopLeftExtension', BootstrapUtilities(
        BootstrapUtilities.paddings,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopRightExtension', BootstrapUtilities(
        BootstrapUtilities.paddings,
    ))
    config['plugins_with_extra_mixins'].setdefault('ShopAddToCartPlugin', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_mixins'].setdefault('BootstrapButtonPlugin', BootstrapUtilities(
        BootstrapUtilities.floats,
    ))

    config['plugins_with_extra_mixins'].setdefault('ShopNavbarSearchForm', BootstrapUtilities(
        BootstrapUtilities.margins,
    ))
    config['plugins_with_extra_fields'].setdefault('ShopNavbarSearchForm', PluginExtraFieldsConfig(
        css_classes={
            'multiple': True,
            'class_names': ['shop-search-form'],
        },
    ))
    config['plugins_with_extra_fields'].setdefault('ShopNavbarCart', PluginExtraFieldsConfig(
        css_classes={
            'multiple': True,
            'class_names': ['shop-secondary-menu'],
        },
    ))
    config['plugins_with_extra_fields'].setdefault('BootstrapNavBrandPlugin', PluginExtraFieldsConfig(
        css_classes={
            'multiple': True,
            'class_names': ['shop-brand-icon'],
        },
    ))
    config['plugins_with_extra_fields'].setdefault('BootstrapNavItemsMainMenuPlugin', PluginExtraFieldsConfig(
        css_classes={
            'multiple': True,
            'class_names': ['shop-primary-menu'],
        },
    ))
    config['plugins_with_extra_render_templates'].setdefault('BootstrapButtonPlugin', [
        ('shop/button.html', _("Responsive Feedback")),
        ('cascade/bootstrap4/button.html', _("Default")),
    ])
