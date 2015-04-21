# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopCartPlugin(ShopPluginBase):
    name = _("Cart")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(_("The Shopping Cart"))

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/cart/cart.html'.format(shop_settings.APP_LABEL),
            'shop/cart/cart.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopCartPlugin)
