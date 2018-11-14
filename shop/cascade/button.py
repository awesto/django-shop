# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap4.buttons import BootstrapButtonPlugin
from cmsplugin_cascade.link.config import LinkElementMixin


class BootstrapRespondingButtonPlugin(BootstrapButtonPlugin):
    model_mixins = (LinkElementMixin,)

    @classmethod
    def get_html_tag_attributes(cls, instance):
        html_tag_attributes = super(BootstrapRespondingButtonPlugin, cls).get_html_tag_attributes(instance)
        html_tag_attributes['ng-click'] = 'showOK()'
        return html_tag_attributes

plugin_pool.unregister_plugin(BootstrapButtonPlugin)
plugin_pool.register_plugin(BootstrapRespondingButtonPlugin)
