# -*- coding: utf-8 -*-
from django import template
from classytags.helpers import InclusionTag

from shop.util.cart import get_or_create_cart


register = template.Library()


class Cart(InclusionTag):
    """
    Inclusion tag for displaying cart summary.
    """
    template = 'shop/templatetags/_cart.html'
    
    def get_context(self, context):
        cart = get_or_create_cart(context['request'])
        return {
            'cart': cart
        } 
register.tag(Cart)