# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal, getcontext
import math
try:
    import cPickle as pickle
except ImportError:
    import pickle
import json

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.six import text_type
from rest_framework import serializers
from shop.money.money_maker import AbstractMoney, MoneyMaker, _make_money
from shop.money.fields import MoneyField as MoneyDbField
from shop.rest.money import MoneyField, JSONRenderer
from myshop.models.manufacturer import Manufacturer
from myshop.models import Commodity


class AbstractMoneyTest(TestCase):

    def test_is_abstract(self):
        self.assertRaises(TypeError, lambda: AbstractMoney(1))


class MoneyMakerTest(TestCase):

    def test_create_money_type_without_arguments(self):
        Money = MoneyMaker()
        money = Money()
        self.assertTrue(money.is_nan())

    def test_create_money_type_with_unknown_currency(self):
        self.assertRaises(ValueError, lambda: MoneyMaker(currency_code="ABC"))

    def test_create_money_type_without_decimal_places(self):
        Money = MoneyMaker(currency_code='JPY')
        self.assertEqual(Money._cents, 0)

    def test_create_instance_with_value_as_none(self):
        Money = MoneyMaker()
        money = Money(value=None)
        self.assertTrue(money.is_nan())

    def test_create_instance_with_invalid_value(self):
        Money = MoneyMaker()
        self.assertRaises(ValueError, lambda: Money(value="invalid"))

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
        value = Decimal('1.2')
        EUR = MoneyMaker('EUR')
        self.assertTrue(issubclass(EUR, Decimal))
        self.assertIsInstance(EUR(value), Decimal)

    def test_str_with_too_much_precision(self):
        EUR = MoneyMaker('EUR')
        value = EUR(1)
        prec = getcontext().prec
        value._cents = Decimal("0." + ("0" * prec))
        self.assertRaises(ValueError, lambda: str(value))

    def test_str(self):
        EUR = MoneyMaker('EUR')
        value = EUR()
        self.assertEqual(text_type(value), "€ –")

    def test_reduce(self):
        Money = MoneyMaker('EUR')
        value = Money()
        func, args = value.__reduce__()
        self.assertTrue(func is _make_money)
        self.assertEqual(args, ("EUR", "NaN"))

        Money = func(*args)
        self.assertTrue(Money.is_nan())

    def test_format(self):
        EUR, JPY = MoneyMaker('EUR'), MoneyMaker('JPY')
        self.assertEqual(format(EUR()), "€ –")
        self.assertEqual(format(JPY()), "¥ –")
        self.assertEqual(format(EUR(1.1)), "€ 1.10")
        self.assertEqual(format(JPY(1)), "¥ 1")

    def test_float_format(self):
        EUR = MoneyMaker('EUR')
        d = Decimal(1.99)
        e = EUR(d)
        self.assertEqual('{}'.format(e), "€ 1.99")
        self.assertEqual('{:}'.format(e), "€ 1.99")
        self.assertEqual('{:f}'.format(e), "€ 1.99")
        self.assertEqual('{:.5}'.format(e), "€ 1.9900")
        self.assertEqual('{:.5f}'.format(e), "€ 1.99000")
        self.assertEqual('{:.20}'.format(e), "€ {:.20}".format(d))
        self.assertEqual('{:.20f}'.format(e), "€ {:.20f}".format(d))

    def test_add(self):
        Money = MoneyMaker()
        self.assertEqual(Money('1.23') + Money(2), Money('3.23'))
        self.assertEqual(Money('1.23') + Money(0), Money('1.23'))
        self.assertEqual(Money(1) + (Money(-1)), Money(0))
        self.assertEqual(Money(1).__radd__(Money(2)), Money(3))

    def test_add_zero(self):
        Money = MoneyMaker()
        self.assertEqual(Money('1.23') + 0, Money('1.23'))
        self.assertEqual(Money('1.23') + 0.0, Money('1.23'))
        self.assertEqual(Money('1.23') + Money('NaN'), Money('1.23'))
        self.assertEqual(0 + Money('1.23'), Money('1.23'))
        self.assertEqual(0.0 + Money('1.23'), Money('1.23'))
        self.assertEqual(Money('NaN') + Money('1.23'), Money('1.23'))
        self.assertRaises(ValueError, lambda: Money(1) + 1)
        self.assertRaises(ValueError, lambda: Money(1) + 1.0)
        self.assertRaises(ValueError, lambda: 1 + Money(1))
        self.assertRaises(ValueError, lambda: 1.0 + Money(1))

    def test_sub(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) - Money(2), Money(-1))
        self.assertRaises(ValueError, lambda: Money(1).__rsub__(Money(2)))

    def test_neg(self):
        Money = MoneyMaker()
        self.assertEqual(- Money(1), Money(-1))
        self.assertEqual(- Money(-1), Money(1))
        self.assertEqual(- Money(0), Money(0))

    def test_mul(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) * 1, Money(1))
        self.assertEqual(Money(1) * 0, Money(0))
        self.assertEqual(Money(1) * -1, Money(-1))
        self.assertEqual(Money(1) * 1, Money(1))
        self.assertEqual(Money(1) * 0, Money(0))
        self.assertEqual(Money(1).__rmul__(-1), Money(-1))
        self.assertEqual(Money(1).__rmul__(1.0), Money(1))
        self.assertEqual(format(Money(1) * None), "€ –")
        self.assertRaises(ValueError, lambda: Money(1) * (Money(1)))

    def test_div(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1) / 2, Money(0.5))
        self.assertEqual(Money(1) / 2.0, Money(0.5))
        self.assertRaises(ValueError, lambda: Money(1) / Money(2))
        self.assertRaises(ValueError, lambda: Money(1).__rdiv__(2))

    def test_truediv(self):
        Money = MoneyMaker()
        self.assertEqual(Money(1).__truediv__(2), Money(0.5))
        self.assertEqual(Money(1).__truediv__(2.0), Money(0.5))
        self.assertRaises(ValueError, lambda: Money(1).__truediv__(Money(2)))
        self.assertRaises(ValueError, lambda: Money(1).__rtruediv__(2))

    def test_pow(self):
        Money = MoneyMaker()
        self.assertRaises(ValueError, lambda: Money(1) ** Money(2))

    def test_float(self):
        Money = MoneyMaker()

        money = Money(Decimal('sNaN'))
        self.assertRaises(ValueError, lambda: float(money))

        money = Money(Decimal('NaN'))
        self.assertTrue(math.isnan(float(money)))

        money = Money(Decimal('-NaN'))
        self.assertTrue(math.isnan(float(money)))

        money = Money(Decimal('1.0'))
        self.assertEqual(float(money), 1.0)

    def test_currency(self):
        Money = MoneyMaker('EUR')
        self.assertEqual(Money.currency, 'EUR')
        self.assertEqual(Money.subunits, 100)
        Money = MoneyMaker('JPY')
        self.assertEqual(Money.currency, 'JPY')
        self.assertEqual(Money.subunits, 1)

    def test_as_decimal(self):
        Money = MoneyMaker()
        money = Money('1.23')
        quantized_decimal = Decimal('1.23').quantize(Decimal('.01'))
        self.assertEqual(money.as_decimal(), quantized_decimal)

    def test_as_integer(self):
        Money = MoneyMaker()
        money = Money('1.23')
        self.assertEqual(money.as_integer(), 123)

    def test_pickle(self):
        Money = MoneyMaker()
        money = Money('1.23')
        pickled = pickle.dumps(money)
        self.assertEqual(pickle.loads(pickled), money)


class MoneyDbFieldTests(TestCase):
    def test_to_python(self):
        EUR = MoneyMaker('EUR')
        f = MoneyDbField(currency='EUR', null=True)
        self.assertEqual(f.to_python(3), EUR('3'))
        self.assertEqual(f.to_python('3.14'), EUR('3.14'))
        self.assertEqual(f.to_python(None), EUR())
        with self.assertRaises(ValidationError):
            f.to_python('abc')

    def test_default(self):
        EUR = MoneyMaker('EUR')
        f = MoneyDbField(currency='EUR', null=False)
        self.assertEqual(f.get_default(), EUR())
        f = MoneyDbField(currency='EUR', null=True)
        self.assertEqual(f.get_default(), EUR())
        f = MoneyDbField(currency='EUR')
        self.assertEqual(f.get_default(), EUR())

    def test_format(self):
        f = MoneyDbField(max_digits=5, decimal_places=3)
        self.assertEqual(f._format(f.to_python(2)), '2.000')
        self.assertEqual(f._format(f.to_python('2.34567')), '2.346')
        self.assertEqual(f._format(None), None)

    def test_filter_with_strings(self):
        amount = MoneyMaker('EUR')('12.34')
        m1 = Manufacturer(name="Rosebutt")
        m1.save()
        bag = Commodity.objects.create(unit_price=amount, product_code='B', order=1, product_name="Bag",
                                       slug='bag', manufacturer=m1, caption="This is a bag")
        self.assertEqual(list(Commodity.objects.filter(unit_price='12.34')), [bag])
        self.assertEqual(list(Commodity.objects.filter(unit_price='12.35')), [])
        self.assertEqual(list(Commodity.objects.filter(unit_price__gt='12.33')), [bag])
        self.assertEqual(list(Commodity.objects.filter(unit_price__gt='12.34')), [])
        self.assertEqual(list(Commodity.objects.filter(unit_price__gte='12.34')), [bag])
        self.assertEqual(list(Commodity.objects.filter(unit_price__lt='12.35')), [bag])
        self.assertEqual(list(Commodity.objects.filter(unit_price__lt='12.34')), [])
        self.assertEqual(list(Commodity.objects.filter(unit_price__lte='12.34')), [bag])


class MoneyTestSerializer(serializers.Serializer):
    amount = MoneyField(read_only=True)


class MoneySerializerTests(TestCase):
    def test_rest(self):
        EUR = MoneyMaker('EUR')
        instance = type(str('TestMoney'), (object,), {'amount': EUR('1.23')})
        serializer = MoneyTestSerializer(instance)
        self.assertDictEqual({'amount': '€ 1.23'}, serializer.data)

    def test_json(self):
        EUR = MoneyMaker('EUR')
        renderer = JSONRenderer()
        data = {'amount': EUR('1.23')}
        rendered_json = renderer.render(data, 'application/json')
        self.assertDictEqual({'amount': "€ 1.23"}, json.loads(rendered_json.decode('utf-8')))
