# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal, InvalidOperation
from django import template
from django.utils.formats import number_format

register = template.Library()


@register.filter(name='currency')
def currency_filter(price, currency, unpriced=False):
    """
    Prepends the currency to a price.
    If unpriced is True and the price is false or 0, render 'CUR –' instead
    of 'CUR 0.00'
    """
    try:
        value = Decimal(price)
    except InvalidOperation:
        if not price:
            return '%s –' % currency
        value = Decimal(0)
    return '%s %s' % (number_format(value.quantize(Decimal('.00'))), currency)
