# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django import template
from django.conf import settings
from django.template.loader import select_template
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.dateformat import format, time_format
from rest_framework.utils.serializer_helpers import ReturnDict
from classytags.helpers import InclusionTag
from shop import settings as shop_settings
from shop.models.cart import CartModel
from shop.rest.money import JSONRenderer

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
    if not isinstance(value, ReturnDict):
        raise ValueError("Given value must be of type `ReturnDict`")
    data = JSONRenderer().render(value)
    return mark_safe(data)
