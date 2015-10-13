# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal, getcontext
import math

from django.test import TestCase

from shop.money.money_maker import AbstractMoney, MoneyMaker, _make_money


class AbstractMoneyTest(TestCase):

    def test_is_abstract(self):
        self.assertRaises(TypeError, lambda: AbstractMoney(1))


class MoneyMakerTest(TestCase):

    def test_create_new_money_type_without_argumens(self):
        Money = MoneyMaker()
        money = Money()
        self.assertTrue(money.is_nan())

    def test_wrong_currency_raises_assertion_error(self):
        # If we try to call a money class with a value that has a
        # different currency than the class, and the value is an
        # instance of the money class, there should be an
        # AssertionError.
        Money = MoneyMaker(currency_code="EUR")
        value = Money()
        value._currency_code = "USD"
        self.assertRaises(AssertionError, lambda: Money(value))

    def test_create_instance_from_decimal(self):
        Money = MoneyMaker()
        value = Decimal("1.2")
        inst = Money(value)
        self.assertEquals(inst, value)

    def test_unicode_with_value(self):
        Money = MoneyMaker()
        value = Money(1)
        self.assertEqual(unicode(value), "€ 1.00")

    def test_unicode_with_nan(self):
        Money = MoneyMaker()
        value = Money()
        self.assertEqual(unicode(value), "€ –")

    def test_str(self):
        Money = MoneyMaker()
        value = Money()
        self.assertEqual(str(value), "€ –".encode("utf-8"))

    def test_reduce(self):
        Money = MoneyMaker()
        value = Money()
        func, args = value.__reduce__()
        self.assertTrue(func is _make_money)
        self.assertEqual(args, ("EUR", "NaN"))

    def test_format(self):
        Money = MoneyMaker()
        self.assertEqual(format(Money()), "€ –")
        self.assertEqual(format(Money(1)), "€ 1.00")

    def test_format_with_context(self):
        # This uses Decimal.__format__
        Money = MoneyMaker()
        self.assertEqual(Money(1).__format__("", getcontext()), "€ 1")

    def test_add(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__add__(Money(2)), Money(3))
        self.assertEqual(Money(1).__add__(Money(0)), Money(1))
        self.assertEqual(Money(1).__add__(Money(-1)), Money(0))
        self.assertEqual(Money(1).__radd__(Money(2)), Money(3))

    def test_sub(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__sub__(Money(2)), Money(-1))
        self.assertRaises(ValueError, lambda: Money(1).__rsub__(Money(2)))

    def test_neg(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__neg__(), -1)
        self.assertEqual(Money(-1).__neg__(), 1)
        self.assertEqual(Money(0).__neg__(), 0)

    def test_mul(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__mul__(1), Money(1))
        self.assertEqual(Money(1).__mul__(0), Money(0))
        self.assertEqual(Money(1).__mul__(-1), Money(-1))
        self.assertEqual(Money(1).__rmul__(1), Money(1))
        self.assertEqual(Money(1).__rmul__(0), Money(0))
        self.assertEqual(Money(1).__rmul__(-1), Money(-1))
        self.assertEqual(unicode(Money(1).__mul__(None)), "€ –")

    def test_div(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__div__(2), Money(0.5))
        self.assertEqual(Money(1).__div__(2.0), Money(0.5))
        self.assertRaises(ValueError, lambda: Money(1).__div__(Money(2)))
        self.assertRaises(ValueError, lambda: Money(1).__rdiv__(2))

    def test_truediv(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__truediv__(2), Money(0.5))
        self.assertEqual(Money(1).__truediv__(2.0), Money(0.5))
        self.assertRaises(ValueError, lambda: Money(1).__truediv__(Money(2)))
        self.assertRaises(ValueError, lambda: Money(1).__rtruediv__(2))

    def test_pow(self):
        Money = MoneyMaker()
        self.assertRaises(ValueError, lambda: Money(1).__pow__(Money(2)))

    def test_float(self):
        Money = MoneyMaker()

        money = Money(Decimal('sNaN'))
        self.assertRaises(ValueError, lambda: money.__float__())

        money = Money(Decimal('NaN'))
        self.assertTrue(math.isnan(money.__float__()))

        money = Money(Decimal('-NaN'))
        self.assertTrue(math.isnan(money.__float__()))

        money = Money(Decimal('1.0'))
        self.assertEqual(money.__float__(), 1.0)
