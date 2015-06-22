# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from shop import settings as shop_settings
from shop.models.cart import CartModel
from shop.rest.serializers import CartSerializer
from .plugin_base import ShopPluginBase


class ShopCartPlugin(ShopPluginBase):
    name = _("Cart")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'ProcessStepPlugin',)
    cache = False
    CHOICES = (('editable', _("Editable cart")), ('static', _("Static cart")), ('summary', _("Cart summary")),)
    glossary_fields = (
        PartialFormField('render_type',
            widgets.RadioSelect(choices=CHOICES),
            label=_("Render as"),
            initial='editable',
            help_text=_("Shall the cart be editable or a static summary?"),
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        render_type = obj.glossary.get('render_type')
        return mark_safe(dict(cls.CHOICES).get(render_type, ''))

    def get_render_template(self, context, instance, placeholder):
        render_type = instance.glossary.get('render_type')
        if render_type == 'static':
            template_names = [
                '{}/cart/static-cart.html'.format(shop_settings.APP_LABEL),
                'shop/cart/static-cart.html',
            ]
        elif render_type == 'summary':
            template_names = [
                '{}/cart/cart-summary.html'.format(shop_settings.APP_LABEL),
                'shop/cart/cart-summary.html',
            ]
        else:
            template_names = [
                '{}/cart/editable-cart.html'.format(shop_settings.APP_LABEL),
                'shop/cart/editable-cart.html',
            ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        render_type = instance.glossary.get('render_type')
        if render_type in ('static', 'summary',):
            # update context for static cart rendering, if editable the form is updated via Ajax
            cart = CartModel.objects.get_from_request(context['request'])
            cart_serializer = CartSerializer(cart, context=context, label='cart')
            context['cart'] = cart_serializer.data
            if render_type == 'summary':
                # for a cart summary we're only interested into the number of items
                context['cart']['items'] = len(context['cart']['items'])
        return super(ShopCartPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCartPlugin)
