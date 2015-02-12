# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase


class ShopCartPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Cart")
    require_parent = False
    render_template = 'shop/cart.html'

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(_("The Shopping Cart"))

plugin_pool.register_plugin(ShopCartPlugin)
