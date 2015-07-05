# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.forms.models import ModelForm
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
from cmsplugin_cascade.link.forms import TextLinkForm
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from cmsplugin_cascade.mixins import TransparentMixin
from shop.cascade.plugin_base import ShopPluginBase, ShopLinkPluginBase
from shop import settings as shop_settings


class ProcessBarForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Steps"),
        help_text=_("Number of steps for this proceed bar."))


class ProcessBarPlugin(TransparentMixin, ShopPluginBase):
    name = _("Process Bar")
    form = ProcessBarForm
    parent_classes = ('BootstrapRowPlugin', 'BootstrapColumnPlugin',)
    require_parent = True
    allow_children = True

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


class ProcessStepPlugin(TransparentMixin, ShopPluginBase):
    name = _("Process Step")
    parent_classes = ('ProcessBarPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True
    render_template = 'cascade/generic/wrapper.html'
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
        child_classes = super(ProcessStepPlugin, self).get_child_classes(slot, page)
        child_classes += ('ProcessNextStepPlugin',)
        return child_classes

plugin_pool.register_plugin(ProcessStepPlugin)


class ProcessNextStepForm(TextLinkForm):
        LINK_TYPE_CHOICES = (('NEXT_STEP', ("Next Step")), ('cmspage', _("CMS Page")),
            ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)


class ProcessFinalStepForm(TextLinkForm):
        LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")),
            ('PURCHASE_NOW', _("Purchase Now")),)


class ProcessNextStepPlugin(BootstrapButtonMixin, ShopLinkPluginBase):
    name = _("Next Step Button")
    parent_classes = ('ProcessStepPlugin',)
    model_mixins = (LinkElementMixin,)
    fields = ('link_content', ('link_type', 'cms_page',), 'glossary',)

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('link_content', ''))

    def get_form(self, request, obj=None, **kwargs):
        if obj is None or obj.get_parent() is None or obj.get_parent().get_next_sibling():
            kwargs.update(form=ProcessNextStepForm)
        else:
            kwargs.update(form=ProcessFinalStepForm)
        form = super(ProcessNextStepPlugin, self).get_form(request, obj, **kwargs)
        return form

    def get_render_template(self, context, instance, placeholder):
        link_type = instance.glossary.get('link', {}).get('type')
        if link_type == 'NEXT_STEP':
            template_names = [
                '{}/checkout/process-next-step.html'.format(shop_settings.APP_LABEL),
                'shop/checkout/process-next-step.html',
            ]
        elif link_type == 'PURCHASE_NOW':
            template_names = [
                '{}/checkout/process-final-step.html'.format(shop_settings.APP_LABEL),
                'shop/checkout/process-final-step.html',
            ]
        else:
            template_names = [
                '{}/checkout/proceed-button.html'.format(shop_settings.APP_LABEL),
                'shop/checkout/proceed-button.html',
            ]
        return select_template(template_names)

plugin_pool.register_plugin(ProcessNextStepPlugin)
