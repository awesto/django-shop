# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from shop import settings as shop_settings
from shop.models.order import OrderModel
from shop.rest.serializers import OrderListSerializer
from .plugin_base import ShopPluginBase


class ShopOrderPlugin(ShopPluginBase):
    name = _("Order")
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(_("The Order"))

    def get_render_template(self, context, instance, placeholder):
        template_names = [
            '{}/order/order-list.html'.format(shop_settings.APP_LABEL),
            'shop/order/order-list.html',
        ]
        return select_template(template_names)

    def render(self, context, instance, placeholder):
        # update context for static cart rendering, if editable the form is updated via Ajax
        order = OrderModel.objects.get_from_request(context['request'])
        order_serializer = OrderListSerializer(order, context=context, label='order')
        context['order'] = order_serializer.data
        return super(ShopOrderPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(ShopOrderPlugin)
