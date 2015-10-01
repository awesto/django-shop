# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.core.exceptions import ValidationError
from django import forms
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.widgets import TextEditorWidget
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.cms_plugins import TextLinkPlugin
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopSearchResultsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ShopSearchResultsForm, self).clean()
        if self.instance.page and self.instance.page.application_urls != 'ProductSearchApp':
            raise ValidationError("This plugin only makes sense if used on a CMS page with an application of type 'Search'.")
        return cleaned_data


class ShopSearchResultsPlugin(ShopPluginBase):
    name = _("Search Results")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    form = ShopSearchResultsForm
    fields = ('glossary',)
    change_form_template = 'cascade/admin/text_plugin_change_form.html'
    html_parser = HTMLParser()

    def get_render_template(self, context, instance, placeholder):
        return select_template([
                '{}/search/results.html'.format(shop_settings.APP_LABEL),
                'shop/search/results.html',
        ])

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            caption_noresults = self.html_parser.unescape(obj.glossary.get('caption_noresults', ''))
            obj.glossary.update(caption_noresults=caption_noresults)
            # define glossary fields on the fly, because the TextEditorWidget requires the plugin_pk
            text_editor_widget = TextEditorWidget(installed_plugins=[TextLinkPlugin], pk=obj.pk,
                                           placeholder=obj.placeholder, plugin_language=obj.language)
            glossary_fields = (
                PartialFormField('caption_noresults', text_editor_widget, label=_("No Results"),
                    help_text=_("Content which is displayed if search did not find any results."),
                ),
            )
            kwargs.update(glossary_fields=glossary_fields)
        return super(ShopSearchResultsPlugin, self).get_form(request, obj, **kwargs)

plugin_pool.register_plugin(ShopSearchResultsPlugin)
