from django.core.exceptions import ValidationError
from django.forms import fields
from django.template import engines
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _, ugettext
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
        help_text=_("Shall the list of search results use a paginator or scroll infinitely?"),
    )

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
        if instance.placeholder.page.application_urls == 'CatalogSearchApp':
            return select_template([
                '{}/search/results.html'.format(app_settings.APP_LABEL),
                'shop/search/results.html',
            ])
        alert_msg = '''<div class="alert alert-danger">
        This {} plugin is used on a CMS page without an application of type "Search".
        </div>'''
        return engines['django'].from_string(alert_msg.format(self.name))

    def render(self, context, instance, placeholder):
        super(ShopSearchResultsPlugin, self).render(context, instance, placeholder)
        context['pagination'] = instance.glossary.get('pagination', 'paginator')
        return context

    @classmethod
    def get_identifier(cls, obj):
        pagination = obj.glossary.get('pagination')
        if pagination == 'paginator':
            return ugettext("Manual Pagination")
        return ugettext("Infinite Scroll")

plugin_pool.register_plugin(ShopSearchResultsPlugin)
