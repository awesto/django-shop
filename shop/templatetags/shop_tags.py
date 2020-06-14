from collections import OrderedDict
from django import template
from django.conf import settings
from django.template import Node, TemplateSyntaxError
from django.template.loader import select_template
from django.utils import formats
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.dateformat import format, time_format
from django.utils.timezone import datetime
from shop.conf import app_settings
from shop.models.cart import CartModel
from shop.serializers.cart import CartSerializer, CartItems
from shop.rest.money import JSONRenderer

register = template.Library()


class CartIcon(Node):
    """
    Inclusion tag for displaying cart summary.
    """
    def __init__(self, with_items):
        self.with_items = with_items

    def get_template(self):
        return select_template([
            '{}/templatetags/cart-icon.html'.format(app_settings.APP_LABEL),
            'shop/templatetags/cart-icon.html',
        ]).template

    def render(self, context):
        try:
            cart = CartModel.objects.get_from_request(context['request'])
            serializer = CartSerializer(instance=cart, context=context, label='dropdown', with_items=self.with_items)
            cart_data = JSONRenderer().render(serializer.data)
        except CartModel.DoesNotExist:
            cart_data = {'total_quantity': 0, 'num_items': 0}
        context.update({
            'cart_as_json': mark_safe(force_str(cart_data)),
            'has_dropdown': self.with_items != CartItems.without,
        })
        return self.get_template().render(context)


@register.tag
def cart_icon(parser, token):
    def raise_syntax_error():
        choices = '|'.join([item.name for item in CartItems])
        raise TemplateSyntaxError("Template tag '{}' takes one optional argument: {}".format(bits[0], choices))

    bits = token.split_contents()
    if len(bits) > 2:
        raise_syntax_error()
    if len(bits) == 2:
        try:
            with_items = CartItems(bits[1])
        except ValueError:
            raise_syntax_error()
    else:
        with_items = CartItems.without
    return CartIcon(with_items)


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
    if isinstance(value, (dict, OrderedDict, list, tuple)):
        data = JSONRenderer().render(value)
    elif not value:
        data = '{}'
    else:
        msg = "Given value must be of type dict, OrderedDict, list or tuple but it is {}."
        raise ValueError(msg.format(value.__class__.__name__))
    return mark_safe(force_str(data))
