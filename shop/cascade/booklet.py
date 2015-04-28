# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.db.models import get_model
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.fields import IntegerField
from django.template.loader import select_template
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.widgets import NumberInputWidget
from shop.cascade.plugin_base import ShopPluginBase, ButtonPluginBase
from shop import settings as shop_settings


class BookletForm(ManageChildrenFormMixin, LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)

    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Booklet"),
        help_text=_("Number of pages for this booklet."))


class DialogBookletPlugin(ShopPluginBase):
    name = _("Dialog Booklet")
    form = BookletForm
    default_css_class = 'btn-group btn-breadcrumb'
    parent_classes = ('BootstrapRowPlugin', 'BootstrapColumnPlugin',)
    require_parent = True
    allow_children = True
    fields = ('num_children', 'glossary',)
    model_mixins = (LinkElementMixin,)
    fields = (('link_type', 'cms_page'), 'num_children', 'glossary',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(DialogBookletPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} page', 'with {0} pages', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    @classmethod
    def get_link(cls, obj):
        link = obj.glossary.get('link', {})
        if link.get('type') == 'cmspage':
            if 'model' in link and 'pk' in link:
                if not hasattr(obj, '_link_model'):
                    Model = get_model(*link['model'].split('.'))
                    try:
                        obj._link_model = Model.objects.get(pk=link['pk'])
                    except Model.DoesNotExist:
                        obj._link_model = None
                if obj._link_model:
                    return obj._link_model.get_absolute_url()
        else:
            # use the link type as special action keyword
            return link.get('type')

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/booklet.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/booklet.html',
        ]
        return select_template(template_names)

    def get_ring_bases(self):
        bases = super(DialogBookletPlugin, self).get_ring_bases()
        bases.append('LinkPluginBase')
        return bases

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(DialogBookletPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, DialogPagePlugin)

plugin_pool.register_plugin(DialogBookletPlugin)


class DialogPagePlugin(ShopPluginBase):
    name = _("Dialog Page")
    parent_classes = ('DialogBookletPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True
    glossary_fields = (
        PartialFormField('page_title',
            widgets.TextInput(attrs={'size': 150}),
            label=_('Page Title')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(DialogPagePlugin, cls).get_identifier(obj)
        content = obj.glossary.get('page_title', '')
        if content:
            content = unicode(Truncator(content).words(3, truncate=' ...'))
        return format_html('{0}{1}', identifier, content)

    def get_child_classes(self, slot, page):
        """
        Bypass allowed children from grandparent plugin.
        """
        instance = self.cms_plugin_instance
        if instance and instance.parent and instance.parent.parent:
            plugin_class = instance.parent.parent.get_plugin_class()
            child_classes = plugin_class().get_child_classes(slot, page)
        else:
            child_classes = super(DialogBookletPlugin, self).get_child_classes(slot, page)
        child_classes += ('BookletProceedButtonPlugin',)
        return child_classes

plugin_pool.register_plugin(DialogPagePlugin)


class BookletProceedButtonPlugin(ButtonPluginBase):
    name = _("Booklet Proceed Button")
    parent_classes = ('DialogPagePlugin',)
    model_mixins = (LinkElementMixin,)
    glossary_fields = (
        PartialFormField('button_content',
            widgets.TextInput(),
            label=_("Content"),
            help_text=_("Proceed to next page of this booklet."),
        ),
    ) + ButtonPluginBase.glossary_fields

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/booklet-next-page.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/booklet-next-page.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(BookletProceedButtonPlugin)
