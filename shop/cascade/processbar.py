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
from cmsplugin_cascade.link.forms import LinkForm, TextLinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.widgets import NumberInputWidget
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from cmsplugin_cascade.mixins import TransparentMixin
from shop.cascade.plugin_base import ShopPluginBase, ShopButtonPluginBase
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


class ProcessNextStepPlugin(BootstrapButtonMixin, ShopButtonPluginBase):
    name = _("Next Step Button")
    parent_classes = ('ProcessStepPlugin',)
    model_mixins = (LinkElementMixin,)

    def get_form(self, request, obj=None, **kwargs):
        """
        Build edit form during runtime, since the link type depends on the position of this plugin.
        """
        link_content = CharField(label=_("Button Content"))
        if obj and obj.get_parent() and obj.get_parent().get_next_sibling():
            LINK_TYPE_CHOICES = (('NEXT_STEP', ("Next Step")), ('cmspage', _("CMS Page")),
                ('RELOAD_PAGE', _("Reload Page")), ('PURCHASE_NOW', _("Purchase Now")),)
        else:
            LINK_TYPE_CHOICES = (('cmspage', _("CMS Page")), ('RELOAD_PAGE', _("Reload Page")),
                ('PURCHASE_NOW', _("Purchase Now")),)
        Form = type(str('ProcessNextStepForm'), (TextLinkFormMixin, LinkForm.get_form_class(),),
            {'link_content': link_content, 'LINK_TYPE_CHOICES': LINK_TYPE_CHOICES})
        kwargs.update(form=Form)
        return super(ProcessNextStepPlugin, self).get_form(request, obj, **kwargs)

    def get_render_template(self, context, instance, placeholder):
        link_type = instance.glossary.get('link', {}).get('type')
        if link_type == 'NEXT_STEP':
            template_names = [
                '{}/checkout/process-next-step.html'.format(shop_settings.APP_LABEL),
                'shop/checkout/process-next-step.html',
            ]
        elif link_type == 'PURCHASE_NOW':
            template_names = [
                '{}/checkout/process-purchase-now.html'.format(shop_settings.APP_LABEL),
                'shop/checkout/process-purchase-now.html',
            ]
        else:
            template_names = [
                '{}/checkout/proceed-button.html'.format(shop_settings.APP_LABEL),
                'shop/checkout/proceed-button.html',
            ]
        return select_template(template_names)

plugin_pool.register_plugin(ProcessNextStepPlugin)
