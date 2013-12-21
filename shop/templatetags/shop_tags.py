# -*- coding: utf-8 -*-
from copy import copy
from django import template

from shop.util.cart import get_or_create_cart
from shop.models.productmodel import Product

from django.conf import settings


register = template.Library()


@register.inclusion_tag('shop/templatetags/_cart.html', takes_context=True)
def cart(context):
    """Inclusion tag for displaying cart summary."""
    request = context['request']
    cart = get_or_create_cart(request)
    cart.update(request)
    return {
        'cart': cart
    }


@register.inclusion_tag('shop/templatetags/_order.html', takes_context=True)
def order(context, order):
    """Inclusion tag for displaying order."""
    if context.has_key("order"):
        # do not overwrite already presented order
        duplicate = copy(context)
        duplicate.update({"order": order,})
        return duplicate
    context.update({"order": order,})
    return context


@register.inclusion_tag('shop/templatetags/_products.html', takes_context=True)
def products(context, *args):
    """Inclusion tag for displaying all products. Expects one argument - an iterable"""
    if not args:
        context.update({'products': Product.objects.filter(active=True), })
    else:
        if len(args) == 1:
            context.update({'products': args[0], })
        else:
            context.update({'products': args, })
    return context


@register.simple_tag
def priceformat(price):
    FORMAT = getattr(settings, 'SHOP_PRICE_FORMAT', '%0.2f')
    if not price and price != 0:
        return ''
    return FORMAT % price
