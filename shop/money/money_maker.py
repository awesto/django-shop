# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal, InvalidOperation
from django.utils.formats import number_format
from django.utils.encoding import force_text
from shop import settings as shop_settings
from iso4217 import CURRENCIES


class AbstractMoney(Decimal):
    def __new__(cls, value):
        raise TypeError("Can not instantiate {} as AbstractMoney.".format(value))

    def __unicode__(self):
        """
        Renders the price localized and formatted in its current currency.
        """
        try:
            amount = number_format(self.quantize(self._cents))
        except InvalidOperation:
            raise ValueError("Can not represent {} as Money type.".format(self.__repr__()))
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
        return self.__add__(other, context)

    def __sub__(self, other, context=None):
        self._assert_addable(other)
        # self - other is computed as self + other.copy_negate()
        amount = Decimal.__add__(self, other.copy_negate(), context=context)
        return self.__class__(amount)

    def __rsub__(self, other, context=None):
        raise ValueError("Can not substract money from something else.")

    def __neg__(self, context=None):
        amount = Decimal.__neg__(self, context)
        return self.__class__(amount)

    def __mul__(self, other, context=None):
        self._assert_multipliable(other)
        amount = Decimal.__mul__(self, other, context)
        return self.__class__(amount)

    def __rmul__(self, other, context=None):
        return self.__mul__(other, context)

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
        raise ValueError("Can not divide through a currency.")

    def __pow__(self, other, context=None):
        raise ValueError("Can not raise currencies to their power.")

    def __float__(self):
        """Float representation."""
        if self._isnan():
            if self.is_snan():
                raise ValueError("Cannot convert signaling NaN to float")
            s = "-nan" if self._sign else "nan"
        else:
            s = Decimal.__str__(self)
        return float(s)

    @classmethod
    def get_currency(cls):
        return cls._currency_code

    def _assert_addable(self, other):
        if self._currency_code != getattr(other, '_currency_code', None):
            raise ValueError("Can not add/substract money in different currencies.")

    def _assert_multipliable(self, other):
        if hasattr(other, '_currency_code'):
            raise ValueError("Can not multiply currencies.")

    def _assert_dividable(self, other):
        if hasattr(other, '_currency_code'):
            raise ValueError("Can not divide through a currency.")


class MoneyMaker(type):
    """
    Factory for building Decimal types, which keep track of the used currency. This is to avoid
    unintentional price allocations, when combined with decimals or when working in different
    currencies.

    No automatic conversion of currencies has been implemented. This could however be achieved
    quite easily in a separate shop plugin.
    """
    def __new__(cls, currency_code=None):
        def my_new(cls, value='0', context=None):
            """
            Build a class named MoneyIn<currency_code> inheriting from Decimal.
            """
            if isinstance(value, cls):
                assert cls._currency_code == value._currency_code
            if isinstance(value, (cls, Decimal)):
                self = object.__new__(cls)
                self._exp = value._exp
                self._sign = value._sign
                self._int = value._int
                self._is_special = value._is_special
                return self
            try:
                self = Decimal.__new__(cls, value, context)
            except Exception as err:
                raise ValueError(err)
            return self

        if currency_code is None:
            currency_code = shop_settings.DEFAULT_CURRENCY
        if currency_code not in CURRENCIES:
            raise ValueError("'{}' is an unknown currency code. Please check shop/money/iso4217.py".format(currency_code))
        name = str('MoneyIn' + currency_code)
        bases = (AbstractMoney,)
        try:
            cents = Decimal('.' + CURRENCIES[currency_code][1] * '0')
        except InvalidOperation:
            # Currencies with no decimal places, ex. JPY
            cents = Decimal()
        attrs = {'_currency_code': currency_code, '_currency': CURRENCIES[currency_code],
                 '_cents': cents, '__new__': my_new}
        new_class = type(name, bases, attrs)
        return new_class
