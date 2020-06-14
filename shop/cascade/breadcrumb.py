from django.core.exceptions import ImproperlyConfigured
from django.forms import fields, widgets
from django.template import engines, TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cms.apphook_pool import apphook_pool
from cms.plugin_pool import plugin_pool
from shop.conf import app_settings
from shop.cascade.plugin_base import ShopPluginBase


class BreadcrumbPluginForm(EntangledModelFormMixin):
    CHOICES = [
        ('default', _("Default")),
        ('soft-root', _("With “Soft-Root”")),
        ('catalog', _("With Catalog Count")),
    ]

    render_type = fields.ChoiceField(
        choices=CHOICES,
        widget=widgets.RadioSelect,
        label=_("Render as"),
        initial='default',
        help_text=_("Render an alternative Breadcrumb"),
    )

    class Meta:
        entangled_fields = {'glossary': ['render_type']}


class BreadcrumbPlugin(ShopPluginBase):
    name = _("Breadcrumb")
    parent_classes = []
    allow_children = None
    form = BreadcrumbPluginForm

    @classmethod
    def get_identifier(cls, instance):
        render_type = instance.glossary.get('render_type')
        return mark_safe(dict(cls.form.CHOICES).get(render_type, ''))

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
            return super().get_use_cache(context, instance, placeholder)

plugin_pool.register_plugin(BreadcrumbPlugin)
