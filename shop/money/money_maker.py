# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal, InvalidOperation
from django.utils.functional import Promise
from django.utils.formats import number_format
from django.utils.encoding import force_text
from shop import settings as shop_settings
from iso4217 import CURRENCIES


class MoneyMaker(type):
    """
    Factory for building Decimal types, which keep track of the used currency. This is to avoid
    unintentional price allocations, when combined with decimals or when working in different
    currencies.

    No automatic conversion of currencies has been implemented. This could however be achieved
    quite easily in a separate shop plugin.
    """
    def __unicode__(self):
        """
        Renders the price localized and formatted in its current currency.
        """
        try:
            amount = number_format(Decimal(self).quantize(self._cents))
        except InvalidOperation:
            raise ValueError("Can not represent {0} as Money type.".format(self.__repr__()))
        context = dict(code=self._currency_code, symbol=self._currency[2],
                       currency=self._currency[3], amount=amount)
        return force_text(getattr(shop_settings, 'MONEY_FORMAT').format(**context))

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        value = Decimal.__str__(self)
        return "{}('{}')".format(self.__class__.__name__, value)

    def __add__(self, other, context=None):
        self._assert_addable(other)
        amount = Decimal.__add__(self, other, context)
        return self.__class__(amount)

    def __radd__(self, other, context=None):
        self._assert_addable(other)
        amount = Decimal.__add__(self, other, context)
        return self.__class__(amount)

    def __sub__(self, other, context=None):
        self._assert_addable(other)
        amount = Decimal.__sub__(self, other, context)
        return self.__class__(amount)

    def __rsub__(self, other, context=None):
        other._assert_addable(self)
        amount = Decimal.__sub__(other, self, context)
        return self.__class__(amount)

    def __mul__(self, other, context=None):
        self._assert_multipliable(other)
        amount = Decimal.__mul__(self, other, context)
        return self.__class__(amount)

    def __rmul__(self, other, context=None):
        self._assert_multipliable(other)
        amount = Decimal.__mul__(self, other, context)
        return self.__class__(amount)

    def __div__(self, other, context=None):
        self._assert_dividable(other)
        amount = Decimal.__div__(self, other, context)
        return self.__class__(amount)

    def __rdiv__(self, other, context=None):
        raise ValueError("Can not divide through a currency.")

    def __truediv__(self, other, context=None):
        self._assert_dividable(other)
        amount = Decimal.__truediv__(self, other, context)
        return self.__class__(amount)

    def __rtruediv__(self, other, context=None):
        self._assert_dividable(other)
        amount = Decimal.__truediv__(self, other, context)
        return self.__class__(amount)

    def __pow__(self, other, context=None):
        raise ValueError("Can not raise currencies to their power.")

    def _assert_addable(self, other):
        if self._currency_code != getattr(other, '_currency_code', None):
            raise ValueError("Can not add/substract money in different currencies.")

    def _assert_multipliable(self, other):
        if hasattr(other, '_currency_code'):
            raise ValueError("Can not multiply currencies.")

    def _assert_dividable(self, other):
        if hasattr(other, '_currency_code'):
            raise ValueError("Can not divide through a currency.")

    def __new__(cls, currency_code=None):
        """
        Build a class type, which behaves similar to Decimal, but knows about its currency.
        """
        if currency_code is None:
            currency_code = shop_settings.DEFAULT_CURRENCY
        if currency_code not in CURRENCIES:
            raise ValueError("'{}' is an unknown currency code. Please check shop/money/iso4217.py".format(currency_code))
        name = str('MoneyIn' + currency_code)
        # the Promise is required so that the REST JSONEncoder serializes our money type
        bases = (Promise, Decimal)
        cents = Decimal('.' + CURRENCIES[currency_code][1] * '0')
        attrs = dict((k, v) for k, v in cls.__dict__.items() if k != '__new__')
        attrs.update(_currency_code=currency_code, _currency=CURRENCIES[currency_code], _cents=cents)
        new_class = type(name, bases, attrs)
        return new_class
