# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ValidationError
from django.template import Template
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopOrderViewsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ShopOrderViewsForm, self).clean()
        if self.instance.page and self.instance.page.application_urls != 'OrderApp':
            raise ValidationError("This plugin only makes sense if used on a CMS page with an application of type 'OrderApp'.")
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
