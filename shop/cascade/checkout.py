# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase
from shop.models.cart import CartModel
from shop.rest.serializers import CartSerializer


class ShopCheckoutPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout")
    require_parent = False

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(_("The Checkout Form"))

    @property
    def render_template(self):
        template_names = [
            '{}/checkout/main.html'.format(settings.SHOP_APP_LABEL),
            'shop/checkout/main.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        cart = CartModel.objects.get_from_request(context['request'])
        cart_serializer = CartSerializer(cart, context=context, label='checkout')
        context['cart'] = cart_serializer.data
        return super(ShopCheckoutPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutPlugin)
