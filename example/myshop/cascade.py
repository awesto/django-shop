# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.cascade.plugin_base import CatalogLinkForm, CatalogLinkPluginBase
from cmsplugin_cascade.sphinx.link_plugin import SphinxDocsLinkForm, SphinxDocsLinkPlugin


class DocumentationLinkForm(CatalogLinkForm, SphinxDocsLinkForm):
    LINK_TYPE_CHOICES = list(CatalogLinkForm.LINK_TYPE_CHOICES)
    LINK_TYPE_CHOICES.insert(1, SphinxDocsLinkForm.LINK_TYPE_CHOICES[1])


class DocumentationLinkPluginBase(SphinxDocsLinkPlugin, CatalogLinkPluginBase):
    fields = [
        ('link_type', 'cms_page', 'section', 'product', 'documentation', 'ext_url', 'mail_to'),
        'glossary',
    ]
    ring_plugin = 'DocumentationLinkPlugin'

    class Media:
        js = ['myshop/js/admin/link_plugin.js']
