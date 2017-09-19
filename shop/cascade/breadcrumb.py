# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.template import engines, TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _

from cms.apphook_pool import apphook_pool
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField

from shop.conf import app_settings
from .plugin_base import ShopPluginBase


class BreadcrumbPlugin(ShopPluginBase):
    name = _("Breadcrumb")
    CHOICES = (('default', _("Default Breadcrumb")), ('soft-root', _("“Soft-Root” Breadcrumb")),
               ('catalog', _("With Catalog Count")), ('empty', _("Hidden Breadcrumb")),)
    parent_classes = ()
    allow_children = None

    render_type = GlossaryField(
        widgets.RadioSelect(choices=CHOICES),
        label=_("Render as"),
        initial='default',
        help_text=_("Render an alternative Breadcrumb"),
    )

    @classmethod
    def get_identifier(cls, instance):
        render_type = instance.glossary.get('render_type')
        return mark_safe(dict(cls.CHOICES).get(render_type, ''))

    def get_render_template(self, context, instance, placeholder):
        render_type = instance.glossary.get('render_type')
        try:
            return select_template([
                '{}/breadcrumb/{}.html'.format(app_settings.APP_LABEL, render_type),
                'shop/breadcrumb/{}.html'.format(render_type),
            ])
        except TemplateDoesNotExist:
            return engines['django'].from_string('<!-- empty breadcrumb -->')

    def get_use_cache(self, context, instance, placeholder):
        try:
            app = apphook_pool.get_apphook(instance.page.application_urls)
            return app.cache_placeholders
        except (AttributeError, ImproperlyConfigured):
            return super(BreadcrumbPlugin, self).get_use_cache(context, instance, placeholder)

plugin_pool.register_plugin(BreadcrumbPlugin)
