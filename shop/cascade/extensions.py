# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import TransparentContainer

from .plugin_base import ShopPluginBase


class ShopExtendableMixin(object):
    """
    Add this mixin class to the list of ``model_mixins``, in the plugin class wishing to use extensions.
    """
    @property
    def left_extension(self):
        if self.child_plugin_instances is None:
            return
        result = [cp for cp in self.child_plugin_instances if cp.plugin_type == 'ShopLeftExtension']
        if result:
            return result[0]

    @property
    def right_extension(self):
        if self.child_plugin_instances is None:
            return
        result = [cp for cp in self.child_plugin_instances if cp.plugin_type == 'ShopRightExtension']
        if result:
            return result[0]


class LeftRightExtensionMixin(object):
    """
    Plugin classes wishing to use extensions shall inherit from this class.
    """
    @classmethod
    def get_child_classes(cls, slot, page, instance=None):
        child_classes = ['ShopLeftExtension', 'ShopRightExtension', None]
        # allow only one left and one right extension
        for child in instance.get_children():
            child_classes.remove(child.plugin_type)
        return child_classes


class ShopLeftExtension(TransparentContainer, ShopPluginBase):
    name = _("Left Extension")
    require_parent = True
    parent_classes = ('ShopCartPlugin', 'ShopOrderViewsPlugin')
    allow_children = True
    render_template = 'cascade/generic/naked.html'

plugin_pool.register_plugin(ShopLeftExtension)


class ShopRightExtension(TransparentContainer, ShopPluginBase):
    name = _("Right Extension")
    require_parent = True
    parent_classes = ('ShopCartPlugin', 'ShopOrderViewsPlugin')
    allow_children = True
    render_template = 'cascade/generic/naked.html'

plugin_pool.register_plugin(ShopRightExtension)
