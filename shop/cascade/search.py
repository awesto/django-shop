from django.core.exceptions import ValidationError
from django.forms import fields, widgets
from django.template import engines
from django.template.loader import select_template
from django.utils.translation import gettext_lazy as _, gettext
from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from shop.cascade.plugin_base import ShopPluginBase
from shop.conf import app_settings


class ShopSearchResultsFormMixin(EntangledModelFormMixin):
    CHOICES = [
        ('paginator', _("Use Paginator")),
        ('manual', _("Manual Infinite")),
        ('auto', _("Auto Infinite")),
    ]

    pagination = fields.ChoiceField(
        label=_("Pagination"),
        choices=CHOICES,
        widget=widgets.RadioSelect,
        help_text=_("Shall the list of search results use a paginator or scroll infinitely?"),
    )

    class Meta:
        entangled_fields = {'glossary': ['pagination']}

    def clean(self):
        cleaned_data = super().clean()
        page = self.instance.placeholder.page if self.instance.placeholder_id else None
        if page and page.application_urls != 'CatalogSearchApp':
            raise ValidationError("This plugin can only be used on a CMS page with an application of type 'Search'.")
        return cleaned_data


class ShopSearchResultsPlugin(ShopPluginBase):
    name = _("Search Results")
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    form = ShopSearchResultsFormMixin
    cache = False

    def get_render_template(self, context, instance, placeholder):
        if instance.placeholder.page.application_urls != 'CatalogSearchApp':
            alert_msg = '''<div class="alert alert-danger">
            Plugin "{}" is used on a CMS page without an application of type "Catalog Search".
            </div>'''
            return engines['django'].from_string(alert_msg.format(self.name))
        return select_template([
            '{}/search/results.html'.format(app_settings.APP_LABEL),
            'shop/search/results.html',
        ])

    def render(self, context, instance, placeholder):
        self.super(ShopSearchResultsPlugin, self).render(context, instance, placeholder)
        context['pagination'] = instance.glossary.get('pagination', 'paginator')
        return context

    @classmethod
    def get_identifier(cls, obj):
        pagination = obj.glossary.get('pagination')
        if pagination == 'paginator':
            return gettext("Manual Pagination")
        return gettext("Infinite Scroll")

plugin_pool.register_plugin(ShopSearchResultsPlugin)
