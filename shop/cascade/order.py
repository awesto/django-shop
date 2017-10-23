# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.template import engines
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentWrapper

from djng.forms import fields, NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form

from shop.conf import app_settings
from .extensions import ShopExtendableMixin, LeftRightExtensionMixin
from .plugin_base import ShopPluginBase


class ShopOrderViewsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ShopOrderViewsForm, self).clean()
        if self.instance.page and self.instance.page.application_urls != 'OrderApp':
            msg = "This plugin only makes sense if used on a CMS page with an application of type 'OrderApp'."
            raise ValidationError(msg)
        return cleaned_data


class ShopOrderViewsPlugin(LeftRightExtensionMixin, TransparentWrapper, ShopPluginBase):
    name = _("Order Views")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = True
    model_mixins = (ShopExtendableMixin,)
    form = ShopOrderViewsForm
    cache = False

    def get_render_template(self, context, instance, placeholder):
        many = context.get('many')
        if many is True:
            # render Order List View
            return select_template([
                '{}/order/list.html'.format(app_settings.APP_LABEL),
                'shop/order/list.html',
            ])
        if many is False:
            # render Order Detail View
            return select_template([
                '{}/order/detail.html'.format(app_settings.APP_LABEL),
                'shop/order/detail.html',
            ])
        # can happen, if this plugin is abused outside of an OrderView
        return engines['django'].from_string('<pre class="bg-danger">This {} plugin is used on a CMS page without an application of type "View Order".</pre>'.format(self.name))

plugin_pool.register_plugin(ShopOrderViewsPlugin)


class OrderButtonForm(ShopOrderViewsForm):
    button_content = fields.CharField(required=False, label=_("Button Content"),
                                      widget=widgets.TextInput())

    def __init__(self, raw_data=None, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = {'button_content': instance.glossary.get('button_content') }
            kwargs.update(initial=initial)
        super(OrderButtonForm, self).__init__(raw_data, *args, **kwargs)

    def clean(self):
        cleaned_data = super(OrderButtonForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary']['button_content'] = cleaned_data['button_content']
        return cleaned_data


class OrderButtonBase(BootstrapButtonMixin, ShopPluginBase):
    parent_classes = ['ShopOrderViewsPlugin']
    form = OrderButtonForm
    fields = ['button_content', 'glossary']
    glossary_field_order = ['button_type', 'button_size', 'button_options', 'quick_float',
                            'icon_align', 'icon_font', 'symbol']

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, instance):
        return instance.glossary.get('button_content', '')

    def render(self, context, instance, placeholder):
        context = super(OrderButtonBase, self).render(context, instance, placeholder)
        context.update({
            'button_label': instance.glossary.get('button_content', '')
        })
        return context


class ShopReorderButtonPlugin(OrderButtonBase):
    name = _("Reorder Button")

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/order/reorder-button.html'.format(app_settings.APP_LABEL),
            'shop/order/reorder-button.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopReorderButtonPlugin)


class ShopCancelOrderButtonPlugin(OrderButtonBase):
    name = _("Cancel Order Button")

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/order/cancel-button.html'.format(app_settings.APP_LABEL),
            'shop/order/cancel-button.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopCancelOrderButtonPlugin)


class AddendumForm(NgModelFormMixin, Bootstrap3Form):
    annotation = fields.CharField(
        label=_("Supplementary annotation for this Order"),
        widget=widgets.Textarea(attrs={'rows': 2}),
    )


class ShopOrderAddendumFormPlugin(OrderButtonBase):
    name = _("Order Addendum Form")

    show_history = GlossaryField(
         widgets.CheckboxInput(),
         label=_("Show History"),
         initial=True,
         help_text=_("Show historical annotations.")
    )

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/order/addenum-form.html'.format(app_settings.APP_LABEL),
            'shop/order/addenum-form.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        context = super(ShopOrderAddendumFormPlugin, self).render(context, instance, placeholder)
        context.update({
            'addenum_form': AddendumForm(),
            'show_history': instance.glossary.get('show_history', True),
        })
        return context

plugin_pool.register_plugin(ShopOrderAddendumFormPlugin)
