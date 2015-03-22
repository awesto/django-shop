# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from django.utils.module_loading import import_by_path
from cms.plugin_pool import plugin_pool
from shop import settings as shop_settings
from .plugin_base import ShopPluginBase


class ShopLoginPlugin(ShopPluginBase):
    """
    A placeholder plugin which provides a login box to be added to any placeholder.
    """
    name = _("Login Form")
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    def __init__(self, *args, **kwargs):
        super(ShopLoginPlugin, self).__init__(*args, **kwargs)
        self.CustomerForm = import_by_path(shop_settings.CUSTOMER_FORM)

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(cls.name)

    def get_render_template(self, context, instance, placeholder):
        if context['request'].user.is_authenticated():
            template_names = [
                '{}/auth/authenticated.html'.format(shop_settings.APP_LABEL),
                'shop/auth/authenticated.html',
            ]
        else:
            template_names = [
                '{}/auth/login.html'.format(shop_settings.APP_LABEL),
                'shop/auth/login.html',
            ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        user = context['request'].user
        if user.is_authenticated():
            context['customer'] = self.CustomerForm(instance=user)
        # anonymous users get a template without customer form, see `get_render_template`
        return super(ShopLoginPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopLoginPlugin)
