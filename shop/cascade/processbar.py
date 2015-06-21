# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.fields import IntegerField
from django.template.loader import select_template
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from shop.cascade.plugin_base import ShopPluginBase, ShopLinkPluginBase
from shop import settings as shop_settings


class ProcessBarForm(ManageChildrenFormMixin, LinkForm):
    LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)

    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Steps"),
        help_text=_("Number of steps for this proceed bar."))


class ProcessBarPlugin(ShopLinkPluginBase):
    name = _("Process Bar")
    form = ProcessBarForm
    parent_classes = ('BootstrapRowPlugin', 'BootstrapColumnPlugin',)
    require_parent = True
    allow_children = True
    model_mixins = (LinkElementMixin,)
    fields = (('link_type', 'cms_page'), 'num_children', 'glossary',)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ProcessBarPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {} page', 'with {} pages', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/process-bar.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/process-bar.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        super(ProcessBarPlugin, self).render(context, instance, placeholder)
        num_children = instance.get_children().count()
        if num_children > 0:
            context['step_css_width'] = '{:3.2f}%'.format(100. / num_children)
        return context

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(ProcessBarPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, ProcessStepPlugin)

plugin_pool.register_plugin(ProcessBarPlugin)


class ProcessStepPlugin(ShopPluginBase):
    name = _("Process Step")
    parent_classes = ('ProcessBarPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True
    glossary_fields = (
        PartialFormField('step_title',
            widgets.TextInput(attrs={'size': 150}),
            label=_("Step Title")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ProcessStepPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('step_title', '')
        if content:
            content = unicode(Truncator(content).words(3, truncate=' ...'))
        return format_html('{0}{1}', identifier, content)

    def get_child_classes(self, slot, page):
        """
        Bypass allowed children from grandparent plugin.
        """
        instance = self.cms_plugin_instance
        try:
            plugin_class = instance.parent.parent.get_plugin_class()
            child_classes = plugin_class().get_child_classes(slot, page)
        except AttributeError:
            child_classes = super(ProcessStepPlugin, self).get_child_classes(slot, page)
        child_classes += ('BookletProceedButtonPlugin',)
        return child_classes

plugin_pool.register_plugin(ProcessStepPlugin)


class BookletProceedButtonPlugin(BootstrapButtonMixin, ShopPluginBase):
    name = _("Booklet Proceed Button")
    parent_classes = ('ProceedStepPlugin',)
    model_mixins = (LinkElementMixin,)
    glossary_fields = (
        PartialFormField('button_content',
            widgets.TextInput(),
            label=_("Content"),
            help_text=_("Proceed to next page of this booklet."),
        ),
    ) + BootstrapButtonMixin.glossary_fields

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('button_content', ''))

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/booklet-next-page.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/booklet-next-page.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(BookletProceedButtonPlugin)
