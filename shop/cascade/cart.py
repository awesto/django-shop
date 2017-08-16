# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.template.loader import select_template, get_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentContainer, TransparentWrapper

from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.serializers.cart import CartSerializer
from .plugin_base import ShopPluginBase


class ShopExtendableMixin(object):
    @property
    def left_extension(self):
        result = [cp for cp in self.child_plugin_instances if cp.plugin_type == 'ShopLeftExtension']
        if result:
            return result[0]

    @property
    def right_extension(self):
        result = [cp for cp in self.child_plugin_instances if cp.plugin_type == 'ShopRightExtension']
        if result:
            return result[0]


class ShopCartPlugin(TransparentWrapper, ShopPluginBase):
    name = _("Cart")
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
            if render_type in ('static', 'summary',):
                # update context for static and summary cart rendering since items are rendered in HTML
                cart_serializer = CartSerializer(cart, context=context, label='cart')
                context['cart'] = cart_serializer.data
                if render_type == 'summary':
                    # for a cart summary we're only interested into the number of items
                    context['cart']['items'] = len(context['cart']['items'])
        except (KeyError, CartModel.DoesNotExist):
            pass
        return super(ShopCartPlugin, self).render(context, instance, placeholder)

    @classmethod
    def get_child_classes(cls, slot, page, instance=None):
        child_classes = ['ShopLeftExtension', 'ShopRightExtension', None]
        # allow only one left and one right extension
        for child in instance.get_children():
            child_classes.remove(child.plugin_type)
        return child_classes

plugin_pool.register_plugin(ShopCartPlugin)


class ShopLeftExtension(TransparentContainer, ShopPluginBase):
    name = _("Left Extension")
    require_parent = True
    parent_classes = ('ShopCartPlugin',)
    allow_children = True
    render_template = 'cascade/generic/naked.html'

plugin_pool.register_plugin(ShopLeftExtension)


class ShopRightExtension(TransparentContainer, ShopPluginBase):
    name = _("Right Extension")
    require_parent = True
    parent_classes = ('ShopCartPlugin',)
    allow_children = True
    render_template = 'cascade/generic/naked.html'

plugin_pool.register_plugin(ShopRightExtension)
