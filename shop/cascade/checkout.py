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



class ShopCheckoutSummaryPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout Summary")
    require_parent = False
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(cls.name)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/summary.html'.format(settings.SHOP_APP_LABEL),
            'shop/checkout/summary.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        cart = CartModel.objects.get_from_request(context['request'])
        cart_serializer = CartSerializer(cart, context=context, label='checkout')
        context['cart'] = cart_serializer.data
        return super(ShopCheckoutSummaryPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutSummaryPlugin)


class ShopCheckoutAddressPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout Address")
    require_parent = False
    parent_classes = ('BootstrapColumnPlugin',)

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(cls.name)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/address.html'.format(settings.SHOP_APP_LABEL),
            'shop/checkout/address.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        from shop.forms.address import AddressForm
        context['address'] = AddressForm()
        #print context['shipping_address'].as_div()
        return super(ShopCheckoutAddressPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutAddressPlugin)
