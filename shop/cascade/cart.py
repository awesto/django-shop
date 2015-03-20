# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase


class ShopCartPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Cart")
    require_parent = False

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(_("The Shopping Cart"))

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/cart/cart.html'.format(settings.SHOP_APP_LABEL),
            'shop/cart/cart.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopCartPlugin)
