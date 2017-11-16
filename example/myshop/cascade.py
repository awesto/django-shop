# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import fields
from django.utils.translation import ugettext_lazy as _

from django_select2.forms import Select2Widget
from shop.cascade.plugin_base import CatalogLinkForm, CatalogLinkPluginBase


class DocumentationSelect2Widget(Select2Widget):
    def render(self, name, value, attrs=None):
        html = super(DocumentationSelect2Widget, self).render(name, value, attrs=attrs)
        return html


def get_documents_map():
    docsmap_file = os.path.join(settings.DOCS_ROOT, 'docsmap.json')
    if not os.path.exists(docsmap_file):
        return ()
    with io.open(docsmap_file) as fh:
        docs_map = json.load(fh, encoding='utf-8')
    result = []
    for path, title in docs_map.items():
        bits = path.split('/')
        if len(bits) == 2 and bits[1] == 'index':
            result.append((bits[0], title))
        elif bits[0] != 'index':
            result.append((path, title))
    return result


class DocumentationLinkForm(CatalogLinkForm):
    LINK_TYPE_CHOICES = [
        ('cmspage', _("CMS Page")),
        ('product', _("Product")),
        ('documentation', _("Documentation")),
        ('exturl', _("External URL")),
        ('email', _("Mail To")),
    ]

    documentation = fields.ChoiceField(
        required=False,
        label='',
        choices=get_documents_map(),
        widget=Select2Widget,
        help_text=_("An internal link onto a documentation page"),
    )

    def clean_documentation(self):
        if self.cleaned_data.get('link_type') == 'documentation':
            self.cleaned_data['link_data'] = {
                'type': 'documentation',
                'value': self.cleaned_data.get('documentation'),
            }

    def set_initial_documentation(self, initial):
        try:
            initial['documentation'] = initial['link']['value']
        except KeyError:
            pass


class DocumentationLinkPluginBase(CatalogLinkPluginBase):
    fields = [
        ('link_type', 'cms_page', 'section', 'product', 'documentation', 'ext_url', 'mail_to'),
        'glossary',
    ]
    ring_plugin = 'DocumentationLinkPlugin'

    class Media:
        js = ['myshop/js/admin/link_plugin.js']

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if link.get('type') == 'documentation':
            return reverse('documentation', args=(link['value'],))
        else:
            return super(DocumentationLinkPluginBase, cls).get_link(obj)
