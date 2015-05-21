# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.template.loader import select_template
from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument
from shop import settings as shop_settings
from shop.models.cart import CartModel

register = template.Library()


class Cart(InclusionTag):
    """
    Inclusion tag for displaying cart summary.
    """
    def get_template(self, context, **kwargs):
        return select_template([
            '{}/templatetags/cart.html'.format(shop_settings.APP_LABEL),
            'shop/templatetags/cart.html',
        ]).name

    def get_context(self, context):
        request = context['request']
        cart = CartModel.objects.get_from_request(request)
        cart.update(request)
        context['cart'] = cart
        return context
register.tag(Cart)
