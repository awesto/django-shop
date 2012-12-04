# -*- coding: utf-8 -*-
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options, Tag
from classytags.arguments import Argument

from shop.util.cart import get_or_create_cart
from shop.models.productmodel import Product


register = template.Library()


class Cart(InclusionTag):
    """
    Inclusion tag for displaying cart summary.
    """
    template = 'shop/templatetags/_cart.html'

    def get_context(self, context):
        cart = get_or_create_cart(context['request'])
        cart.update()
        return {
            'cart': cart
        }
register.tag(Cart)


class Order(InclusionTag):
    """
    Inclusion tag for displaying order.
    """
    template = 'shop/templatetags/_order.html'
    options = Options(
        Argument('order', resolve=True),
        )

    def get_context(self, context, order):
        return {
            'order': order
        }
register.tag(Order)


class Products(InclusionTag):
    """
    Inclusion tag for displaying all products.
    """
    template = 'shop/templatetags/_products.html'
    options = Options(
        Argument('objects', resolve=True, required=False),
    )

    def get_context(self, context, objects):
        if objects is None:
            objects = Product.objects.filter(active=True)
        context.update({'products': objects, })
        return context
register.tag(Products)

def priceformat(price):
    FORMAT = '%0.2f'
    if not price and price != 0:
        return ''
    return FORMAT % price
register.filter(priceformat)

class Thecart(Tag):
    options = Options(
        'as',
        Argument('varname', required=True, resolve=False)
    )

    def render_tag(self, context, varname):
        cart = get_or_create_cart(context['request'])
        cart.update()
        context[varname] = cart
        return ''
register.tag(Thecart)


class Theproducts(Tag):
    options = Options(
        Argument('objects', required=False, resolve=True),
        'as',
        Argument('varname', required=True, resolve=False)
    )

    def render_tag(self, context, objects, varname):
        if objects is None:
            objects = Product.objects.filter(active=True)
        context[varname] = objects
        return ''
register.tag(Theproducts)
