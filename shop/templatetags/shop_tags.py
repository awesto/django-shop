# -*- coding: utf-8 -*-
from django import template

from shop.util.cart import get_or_create_cart

register = template.Library()


@register.inclusion_tag('shop/templatetags/_cart.html', takes_context=True)
def cart(context):
    '''
    Inclusion tag for displaying cart summary.
    '''
    cart = get_or_create_cart(context['request'])
    return {
        'cart': cart,
        }
