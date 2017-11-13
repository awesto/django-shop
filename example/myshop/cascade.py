# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import fields
from django.utils.translation import ugettext_lazy as _

from shop.cascade.plugin_base import CatalogLinkForm, CatalogLinkPluginBase


class MyShopCatalogLinkForm(CatalogLinkForm):
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('product', _("Product")),
        ('documentation', _("Documentation")),
        ('exturl', _("External URL")),
        ('email', _("Mail To")),
    ]
    documentation = fields.CharField(required=False, label='',
        help_text=_("An internal link onto a documentation page"))

    def clean_documentation(self):
        print(self.cleaned_data['documentation'])


class MyShopLinkPluginBase(CatalogLinkPluginBase):
    fields = [
        ('link_type', 'cms_page', 'section', 'product', 'documentation', 'ext_url', 'mail_to',),
        'glossary',
    ]
    ring_plugin = 'MyShopLinkPlugin'

    class Media:
        # css = {'all': ['shop/css/admin/editplugin.css']}
        js = ['myshop/js/admin/link_plugin.js']
