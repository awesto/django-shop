# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.template import Template
from django.template.loader import select_template, TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class BreadcrumbPlugin(ShopPluginBase):
    name = _("Breadcrumb")
    CHOICES = (('default', _("Default Breadcrumb")), ('soft-root', _("“Soft-Root” Breadcrumb")),
        ('catalog', _("With Catalog Count")), ('empty', _("Empty Breadcrumb")),)
    glossary_fields = (
        PartialFormField('render_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Render as"),
            initial='default',
            help_text=_("Render an alternative Breadcrumb"),
        ),
    )
    parent_classes = ()
    allow_children = None

    def get_render_template(self, context, instance, placeholder):
        render_type = instance.glossary.get('render_type')
        try:
            return select_template([
                '{}/breadcrumb/{}.html'.format(shop_settings.APP_LABEL, render_type),
                'shop/breadcrumb/{}.html'.format(render_type),
            ])
        except TemplateDoesNotExist:
            return Template('<!-- empty breadcrumb -->')

plugin_pool.register_plugin(BreadcrumbPlugin)
