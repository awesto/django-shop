# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase
from shop.forms.auth import CustomerForm


class ShopLoginPlugin(CascadePluginBase):
    """
    A placeholder plugin which provides a login box to be added to any placeholder.
    """
    module = 'Shop'
    name = _("Login Form")
    require_parent = False
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(cls.name)

    def get_render_template(self, context, instance, placeholder):
        if context['request'].user.is_authenticated():
            template_names = [
                '{}/auth/authenticated.html'.format(settings.SHOP_APP_LABEL),
                'shop/auth/authenticated.html',
            ]
        else:
            template_names = [
                '{}/auth/login.html'.format(settings.SHOP_APP_LABEL),
                'shop/auth/login.html',
            ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        user = context['request'].user
        if user.is_authenticated():
            context['customer'] = CustomerForm(instance=user)
        # anonymous users get a template without customer form, see `get_render_template`
        return super(ShopLoginPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopLoginPlugin)
