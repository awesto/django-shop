# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.models import ModelForm
from django.forms.fields import IntegerField
from django.template.loader import select_template
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.widgets import NumberInputWidget
from shop.cascade.plugin_base import ShopPluginBase, ButtonPluginBase
from shop import settings as shop_settings


class BookletForm(ManageChildrenFormMixin, ModelForm):
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

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(DialogBookletPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} page', 'with {0} pages', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/booklet.html'.format(shop_settings.APP_LABEL),
            'shop/booklet.html',
        ]
        return select_template(template_names)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(DialogBookletPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, DialogPagePlugin)

plugin_pool.register_plugin(DialogBookletPlugin)


class BookletPageModelMixin(object):
    def slug(self):
        return self.glossary.get('slug', '')


class DialogPagePlugin(ShopPluginBase):
    name = _("Dialog Page")
    parent_classes = ('DialogBookletPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True
    model_mixins = (BookletPageModelMixin,)
    glossary_fields = (
        PartialFormField('page_title',
            widgets.TextInput(attrs={'size': 150}),
            label=_('Page Title')
        ),
        PartialFormField('slug',
            widgets.TextInput(attrs={'size': 150}),
            label=_('Slug')
        ),
    )

    class Media:
        js = ('admin/js/urlify.js', 'shop/js/admin/bookletplugin.js',)

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

    @classmethod
    def get_link(cls, obj):
        try:
            while True:
                parent = obj.parent
                if issubclass(parent.get_plugin_class(), DialogPagePlugin):
                    return parent.get_next_sibling().get_plugin_instance()[0].slug()
        except AttributeError:
            return ''

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/booklet-next-page.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/booklet-next-page.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        context = super(BookletProceedButtonPlugin, self).render(context, instance, placeholder)
        while True:
            parent = instance.parent
            if issubclass(parent.get_plugin_class(), DialogPagePlugin):
                break
        context['slug'] = parent.get_plugin_instance()[0].slug()
        return context

plugin_pool.register_plugin(BookletProceedButtonPlugin)
