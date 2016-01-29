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
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.forms import TextLinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from cmsplugin_cascade.mixins import TransparentMixin
from shop.cascade.plugin_base import ShopPluginBase
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
    def get_identifier(cls, instance):
        identifier = super(ProcessBarPlugin, cls).get_identifier(instance)
        num_cols = instance.get_children().count()
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
        else:
            content = obj.get_position_in_placeholder()
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(ProcessStepPlugin)


class ProcessNextStepForm(TextLinkFormMixin, ModelForm):
    link_content = CharField(required=False, label=_("Button Content"),
        widget=widgets.TextInput(attrs={'id': 'id_name'}))

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
    fields = ('link_content', 'glossary',)
    model_mixins = (LinkElementMixin,)

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(ProcessNextStepPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('link_content', '')
        return format_html('{0}{1}', identifier, content)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/process-next-step.html'.format(shop_settings.APP_LABEL),
            'shop/checkout/process-next-step.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ProcessNextStepPlugin)
