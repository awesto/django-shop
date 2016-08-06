# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from datetime import datetime
from django import template
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http.request import HttpRequest
from django.template import Context, RequestContext
from django.template.loader import select_template
from django.utils import formats
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.dateformat import format, time_format
from cms.models import Placeholder as PlaceholderModel
from cms.plugin_rendering import render_placeholder
from classytags.arguments import Argument
from classytags.helpers import AsTag, InclusionTag
from classytags.core import Options, Tag
from shop import settings as shop_settings
from shop.models.cart import CartModel
from shop.rest.money import JSONRenderer

register = template.Library()


class CartIcon(InclusionTag):
    """
    Inclusion tag for displaying cart summary.
    """
    def get_template(self, context, **kwargs):
        template = select_template([
            '{}/templatetags/cart-icon.html'.format(shop_settings.APP_LABEL),
            'shop/templatetags/cart-icon.html',
        ])
        return template.template.name

    def get_context(self, context):
        request = context['request']
        try:
            cart = CartModel.objects.get_from_request(request)
            cart.update(request)
            context['cart'] = cart
        except CartModel.DoesNotExist:
            pass
        return context
register.tag(CartIcon)


def from_iso8601(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


@register.filter(expects_localtime=True, is_safe=False)
def date(value, arg=None):
    """
    Alternative implementation to the built-in `date` template filter which also accepts the
    date string in iso-8601 as passed in by the REST serializers.
    """
    if value in (None, ''):
        return ''
    if not isinstance(value, datetime):
        value = from_iso8601(value)
    if arg is None:
        arg = settings.DATE_FORMAT
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''


@register.filter(expects_localtime=True, is_safe=False)
def time(value, arg=None):
    """
    Alternative implementation to the built-in `time` template filter which also accepts the
    date string in iso-8601 as passed in by the REST serializers.
    """
    if value in (None, ''):
        return ''
    if not isinstance(value, datetime):
        value = from_iso8601(value)
    if arg is None:
        arg = settings.TIME_FORMAT
    try:
        return formats.time_format(value, arg)
    except AttributeError:
        try:
            return time_format(value, arg)
        except AttributeError:
            return ''


@register.filter
def rest_json(value, arg=None):
    """
    Renders a `ReturnDict` as used by the REST framework into a safe JSON string.
    """
    if not value:
        return mark_safe('{}')
    if not isinstance(value, (dict, OrderedDict, list, tuple)):
        msg = "Given value must be of type dict, OrderedDict, list or tuple but it is {}."
        raise ValueError(msg.format(value.__class__.__name__))
    data = JSONRenderer().render(value)
    return mark_safe(data)


class RenderPlaceholder(AsTag):
    """
    Render the content of the plugins contained in a placeholder.
    The result can be assigned to a variable within the template's context by using the `as` keyword.
    It behaves in the same way as the `PageAttribute` class, check its docstring for more details.
    """
    name = 'render_placeholder'
    options = Options(
        Argument('placeholder'),
        Argument('width', default=None, required=False),
        'language',
        Argument('language', default=None, required=False),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def get_value(self, context, **kwargs):
        placeholder = kwargs.get('placeholder')
        if not placeholder:
            return ''
        width = kwargs.get('width')
        lang = kwargs.get('language')

        context.push()
        request = HttpRequest()
        request.user = AnonymousUser()
        request.current_page = None
        context['request'] = request
        obj = context.get('object')
        content = render_placeholder(obj.placeholder, context, name_fallback=placeholder, lang=lang,
                                     default=None, editable=True, use_cache=True) #, editable=False, use_cache=False)
        return strip_tags(content)

register.tag(RenderPlaceholder)
