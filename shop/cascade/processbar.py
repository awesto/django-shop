# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.forms.fields import CharField
from django.forms.models import ModelForm
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.fields import IntegerField
from django.template.loader import select_template

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.link.forms import TextLinkFormMixin
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.bootstrap4.buttons import BootstrapButtonMixin
from cmsplugin_cascade.plugin_base import TransparentWrapper, TransparentContainer

from shop.conf import app_settings
from shop.cascade.plugin_base import ShopPluginBase


class ProcessBarForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Steps"),
        help_text=_("Number of steps for this proceed bar."))


class ProcessBarPlugin(TransparentWrapper, ShopPluginBase):
    name = _("Process Bar")
    form = ProcessBarForm
    parent_classes = ('BootstrapColumnPlugin',)
    direct_child_classes = ('ProcessStepPlugin',)
    require_parent = True
    allow_children = True

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(ProcessBarPlugin, cls).get_identifier(instance)
        num_cols = instance.get_children().count()
        content = ungettext_lazy('with {} page', 'with {} pages', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/process-bar.html'.format(app_settings.APP_LABEL),
            'shop/checkout/process-bar.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        self.super(ProcessBarPlugin, self).render(context, instance, placeholder)
        num_children = instance.get_num_children()
        if num_children > 0:
            context['step_css_width'] = '{:3.2f}%'.format(100. / num_children)
        return context

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(ProcessBarPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, ProcessStepPlugin)

plugin_pool.register_plugin(ProcessBarPlugin)


class ProcessStepPlugin(TransparentContainer, ShopPluginBase):
    name = _("Process Step")
    direct_parent_classes = parent_classes = ('ProcessBarPlugin',)
    require_parent = True
    allow_children = True
    alien_child_classes = True
    render_template = 'cascade/generic/wrapper.html'
    step_title = GlossaryField(
        widgets.TextInput(attrs={'size': 50}),
        label=_("Step Title")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ProcessStepPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('step_title', '')
        if content:
            content = Truncator(content).words(3, truncate=' ...')
        else:
            content = obj.get_position_in_placeholder()
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(ProcessStepPlugin)


class ProcessNextStepForm(TextLinkFormMixin, ModelForm):
    link_content = CharField(required=False, label=_("Button Content"), widget=widgets.TextInput())

    def __init__(self, raw_data=None, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = instance and dict(instance.glossary) or {}
        initial.update(kwargs.pop('initial', {}))
        kwargs.update(initial=initial)
        super(ProcessNextStepForm, self).__init__(raw_data, *args, **kwargs)


class ProcessNextStepPlugin(BootstrapButtonMixin, ShopPluginBase):
    name = _("Next Step Button")
    parent_classes = ('ProcessStepPlugin',)
    form = ProcessNextStepForm
    fields = ['link_content', 'glossary']
    ring_plugin = 'ProcessNextStepPlugin'
    glossary_field_order = ['disable_invalid', 'button_type', 'button_size', 'button_options', 'quick_float',
                            'icon_align', 'icon_font', 'symbol']

    disable_invalid = GlossaryField(
        label=_("Disable if invalid"),
        widget=widgets.CheckboxInput(),
        initial='',
        help_text=_("Disable button if any form in this set is invalid"),
    )

    class Media:
        css = {'all': ['cascade/css/admin/bootstrap4-buttons.css', 'cascade/css/admin/iconplugin.css']}
        js = ['shop/js/admin/nextstepplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ProcessNextStepPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('link_content', '')
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/process-next-step.html'.format(app_settings.APP_LABEL),
            'shop/checkout/process-next-step.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ProcessNextStepPlugin)
