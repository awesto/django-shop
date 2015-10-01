# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django import forms
from django.template import Template
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopSearchResultsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ShopSearchResultsForm, self).clean()
        if self.instance.page and self.instance.page.application_urls != 'ProductSearchApp':
            raise ValidationError("This plugin only makes sense on a CMS page with an application of type 'Search'.")
        return cleaned_data


class ShopSearchResultsPlugin(ShopPluginBase):
    name = _("Search Results")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    form = ShopSearchResultsForm
    cache = False

    def get_render_template(self, context, instance, placeholder):
        if instance.page.application_urls == 'ProductSearchApp':
            return select_template([
                    '{}/search/results.html'.format(shop_settings.APP_LABEL),
                    'shop/search/results.html',
            ])
        return Template('<pre class="bg-danger">This {} plugin is used on a CMS page without an application of type "Search".</pre>'.format(self.name))

    def render(self, context, instance, placeholder):
        super(ShopSearchResultsPlugin, self).render(context, instance, placeholder)
        try:
            if context['edit_mode']:
                # prevent scrolling while editing
                context['data']['next'] = None
        finally:
            return context

plugin_pool.register_plugin(ShopSearchResultsPlugin)
