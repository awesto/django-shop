# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django import forms
from django.forms import widgets
from django.template import engines
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _, ugettext

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField

from shop.conf import app_settings
from .plugin_base import ShopPluginBase


class ShopSearchResultsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ShopSearchResultsForm, self).clean()
        page = self.instance.placeholder.page if self.instance.placeholder_id else None
        if page and page.application_urls != 'CatalogSearchApp':
            raise ValidationError("This plugin can only be used on a CMS page with an application of type 'Search'.")
        return cleaned_data


class ShopSearchResultsPlugin(ShopPluginBase):
    name = _("Search Results")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    form = ShopSearchResultsForm
    cache = False

    infinite_scroll = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Infinite Scroll"),
        initial=True,
        help_text=_("Shall the search results scroll infinitely?"),
    )

    def get_render_template(self, context, instance, placeholder):
        if instance.placeholder.page.application_urls == 'CatalogSearchApp':
            return select_template([
                    '{}/search/results.html'.format(app_settings.APP_LABEL),
                    'shop/search/results.html',
            ])
        msg = '<pre class="bg-danger">This {} plugin is used on a CMS page without an application of type "Search".</pre>'
        return engines['django'].from_string(msg.format(self.name))

    def render(self, context, instance, placeholder):
        super(ShopSearchResultsPlugin, self).render(context, instance, placeholder)
        context['infinite_scroll'] = bool(instance.glossary.get('infinite_scroll', True))
        try:
            if context['edit_mode']:
                # prevent scrolling while editing
                context['data']['next'] = None
        finally:
            return context

    @classmethod
    def get_identifier(cls, obj):
        if obj.glossary.get('infinite_scroll', True):
            return ugettext("Infinite Scroll")
        return ugettext("Manual Pagination")

plugin_pool.register_plugin(ShopSearchResultsPlugin)
