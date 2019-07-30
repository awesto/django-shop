# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.template.loader import select_template, get_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentWrapper
from shop.cascade.extensions import ShopExtendableMixin, LeftRightExtensionMixin
from shop.cascade.plugin_base import ShopPluginBase
from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.serializers.cart import CartSerializer


class ShopCartPlugin(LeftRightExtensionMixin, TransparentWrapper, ShopPluginBase):
    name = _("Shopping Cart")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    cache = False
    allow_children = True
    model_mixins = (ShopExtendableMixin,)
    CHOICES = [('editable', _("Editable Cart")), ('static', _("Static Cart")),
               ('summary', _("Cart Summary")), ('watch', _("Watch List"))]

    render_type = GlossaryField(
        widgets.RadioSelect(choices=CHOICES),
        label=_("Render as"),
        initial='editable',
        help_text=_("Shall the cart be editable or a static summary?"),
    )

    @classmethod
    def get_identifier(cls, instance):
        render_type = instance.glossary.get('render_type')
        return mark_safe(dict(cls.CHOICES).get(render_type, ''))

    def get_render_template(self, context, instance, placeholder):
        render_template = instance.glossary.get('render_template')
        if render_template:
            return get_template(render_template)
        render_type = instance.glossary.get('render_type')
        if render_type == 'static':
            template_names = [
                '{}/cart/static.html'.format(app_settings.APP_LABEL),
                'shop/cart/static.html',
            ]
        elif render_type == 'summary':
            template_names = [
                '{}/cart/summary.html'.format(app_settings.APP_LABEL),
                'shop/cart/summary.html',
            ]
        elif render_type == 'watch':
            template_names = [
                '{}/cart/watch.html'.format(app_settings.APP_LABEL),
                'shop/cart/watch.html',
            ]
        else:
            template_names = [
                '{}/cart/editable.html'.format(app_settings.APP_LABEL),
                'shop/cart/editable.html',
            ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            context['is_cart_filled'] = cart.items.exists()
            render_type = instance.glossary['render_type']
            if render_type == 'static':
                # update context for static cart with items to be endered as HTML
                cart_serializer = CartSerializer(cart, context=context, label='cart', with_items=True)
                context['cart'] = cart_serializer.data
            elif render_type == 'summary':
                # update context for cart summary to be endered as HTML
                cart_serializer = CartSerializer(cart, context=context, label='cart')
                context['cart'] = cart_serializer.data
        except (KeyError, CartModel.DoesNotExist):
            pass
        return self.super(ShopCartPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopCartPlugin)
