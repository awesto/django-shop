# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal

from django.test import TestCase

from shop.money.money_maker import AbstractMoney, MoneyMaker


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
        Money = MoneyMaker(currency_code='EUR')
        value = Money()
        value._currency_code = 'USD'
        self.assertRaises(AssertionError, lambda: Money(value))

    def test_create_instance_from_decimal(self):
        Money = MoneyMaker()
        value = Decimal("1.2")
        inst = Money(value)
        self.assertEquals(inst, value)

    def test_unicode(self):
        Money = MoneyMaker()
        value = Money(1)
        self.assertEqual(unicode(value), "€ 1.00")
