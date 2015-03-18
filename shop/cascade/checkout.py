# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.fields import PartialFormField
from shop.models.cart import CartModel
from shop.rest.serializers import CartSerializer


class ShopCheckoutSummaryPlugin(CascadePluginBase):
    module = 'Shop'
    name = _("Checkout Summary")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False

    @classmethod
    def get_identifier(cls, obj):
        return force_text(cls.name)

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
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    CHOICES = (('shipping', _("Shipping Address")), ('invoice', _("Invoice Address")),)
    glossary_fields = (
        PartialFormField('address_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Address type"),
            help_text=_("Use this address form for shipping or as invoice."),
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        address_type = obj.glossary.get('address_type')
        address_type = dict(cls.CHOICES).get(address_type)
        return force_text(address_type)

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/checkout/address.html'.format(settings.SHOP_APP_LABEL),
            'shop/checkout/address.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        from shop.forms.address import AddressForm
        from shop.models.address import AddressModel
        addr_type = instance.glossary.get('address_type', 'shipping')
        user = context['request'].user
        priority = 'priority_{}'.format(addr_type)
        address = AddressModel.objects.filter(user=user).order_by(priority).first()
        context['address'] = AddressForm(addr_type, instance=address)
        return super(ShopCheckoutAddressPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCheckoutAddressPlugin)
