# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cmsplugin_cascade.plugin_base import CascadePluginBase


class ShopPluginBase(CascadePluginBase):
    module = 'Shop'
    require_parent = False
    allow_children = False
