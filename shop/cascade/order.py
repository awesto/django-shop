# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import fields, widgets
from django.core.exceptions import ValidationError
from django.template import Template
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap3.buttons import BootstrapButtonMixin
from djng.forms import NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopOrderViewsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ShopOrderViewsForm, self).clean()
        if self.instance.page and self.instance.page.application_urls != 'OrderApp':
            msg = "This plugin only makes sense if used on a CMS page with an application of type 'OrderApp'."
            raise ValidationError(msg)
        return cleaned_data


class ShopOrderViewsPlugin(ShopPluginBase):
    name = _("Order Views")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    form = ShopOrderViewsForm
    cache = False

    def get_render_template(self, context, instance, placeholder):
        many = context.get('many')
        if many is True:
            # render Order List View
            return select_template([
                '{}/order/list.html'.format(shop_settings.APP_LABEL),
                'shop/order/list.html',
            ])
        if many is False:
            # render Order Detail View
            return select_template([
                '{}/order/detail.html'.format(shop_settings.APP_LABEL),
                'shop/order/detail.html',
            ])
        # can happen, if this plugin is abused outside of an OrderView
        return Template('<pre class="bg-danger">This {} plugin is used on a CMS page without an application of type "View Order".</pre>'.format(self.name))

plugin_pool.register_plugin(ShopOrderViewsPlugin)


class ReorderButtonForm(ShopOrderViewsForm):
    button_content = fields.CharField(required=False, label=_("Button Content"),
                                      widget=widgets.TextInput())

    def __init__(self, raw_data=None, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = {'button_content': instance.glossary.get('button_content') }
            kwargs.update(initial=initial)
        super(ReorderButtonForm, self).__init__(raw_data, *args, **kwargs)

    def clean(self):
        cleaned_data = super(ReorderButtonForm, self).clean()
        if self.is_valid():
            cleaned_data['glossary']['button_content'] = cleaned_data['button_content']
        return cleaned_data


class ShopReorderFormPlugin(BootstrapButtonMixin, ShopPluginBase):
    name = _("Reorder Button")
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    form = ReorderButtonForm
    fields = ('button_content', 'glossary',)

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/order/reorder-form.html'.format(shop_settings.APP_LABEL),
            'shop/order/reorder-form.html',
        ]
        return select_template(template_names)

plugin_pool.register_plugin(ShopReorderFormPlugin)


class AddendumForm(NgModelFormMixin, Bootstrap3Form):
    scope_prefix = 'data'
    annotation = fields.CharField(label=_("Supplementary annotation for this Order"), required=False,
                              widget=widgets.Textarea(attrs={'rows': 4}))


class ShopOrderAddendumFormPlugin(BootstrapButtonMixin, ShopPluginBase):
    name = _("Order Addendum Form")
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    form = ReorderButtonForm
    fields = ('button_content', 'glossary',)

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/order/addenum-form.html'.format(shop_settings.APP_LABEL),
            'shop/order/addenum-form.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        super(ShopOrderAddendumFormPlugin, self).render(context, instance, placeholder)
        context['addenum_form'] = AddendumForm()
        return context

plugin_pool.register_plugin(ShopOrderAddendumFormPlugin)
