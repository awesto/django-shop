import pytest
from decimal import Decimal, getcontext
import math
try:
    import cPickle as pickle
except ImportError:
    import pickle
import json

from rest_framework import serializers
from shop.money.money_maker import AbstractMoney, MoneyMaker, _make_money
from shop.rest.money import MoneyField, JSONRenderer

EUR = MoneyMaker('EUR')


def test_is_abstract():
    with pytest.raises(TypeError):
        AbstractMoney(1)


def test_create_money_type_without_arguments():
    Money = MoneyMaker()
    amount = Money()
    assert amount.is_nan() is True


def test_create_money_type_with_unknown_currency():
    with pytest.raises(TypeError):
        MoneyMaker(currency_code="ABC")


def test_create_money_type_without_decimal_places():
    Money = MoneyMaker(currency_code='JPY')
    assert Money._cents == 0


def test_create_instance_with_value_as_none():
    Money = MoneyMaker()
    money = Money(value=None)
    assert money.is_nan() is True

def test_create_instance_with_invalid_value():
    Money = MoneyMaker()
    with pytest.raises(ValueError):
        Money(value="invalid")


def test_wrong_currency_raises_assertion_error():
    # If we try to call a money class with a value that has a
    # different currency than the class, and the value is an
    # instance of the money class, there should be an
    # AssertionError.
    Money = MoneyMaker(currency_code='EUR')
    value = Money()
    value._currency_code = 'USD'
    with pytest.raises(AssertionError):
        Money(value)


def test_create_instance_from_decimal():
    value = Decimal('1.2')
    assert issubclass(EUR, Decimal)
    assert isinstance(EUR(value), Decimal)


def test_str_with_too_much_precision():
    value = EUR(1)
    prec = getcontext().prec
    value._cents = Decimal("0." + ("0" * prec))
    with pytest.raises(ValueError):
        str(value)


def test_thousand_separator(settings):
    value = EUR()
    assert str(value) == "€ –"
    value = EUR('999999.99')
    settings.USE_THOUSAND_SEPARATOR = False
    assert str(value) == "€ 999999.99"
    settings.USE_THOUSAND_SEPARATOR = True
    assert str(value) == "€ 999,999.99"
    settings.LANGUAGE_CODE = 'de'
    assert str(value) == "€ 999.999,99"
    settings.USE_THOUSAND_SEPARATOR = False
    assert str(value) == "€ 999999,99"

def test_check_rounding():
    value = EUR('999999.995')
    assert str(value) == "€ 1000000.00"
    value = EUR('-111111.114')
    assert str(value) == "-€ 111111.11"


def test_check_formatting_currency():
    value = -EUR('111111.11')
    value.MONEY_FORMAT='{minus}{amount} {code}'
    assert str(value) == "-111111.11 EUR"


def test_reduce():
    value = EUR()
    func, args = value.__reduce__()
    assert func is _make_money
    assert args == ("EUR", "NaN")
    Money = func(*args)
    assert Money.is_nan() is True


def test_format():
    JPY = MoneyMaker('JPY')
    assert format(EUR()) == "€ –"
    assert format(JPY()) == "¥ –"
    assert format(EUR(1.1)) == "€ 1.10"
    assert format(JPY(1)) == "¥ 1"


def test_float_format():
    d = Decimal(1.99)
    e = EUR(d)
    assert '{}'.format(e) == "€ 1.99"
    assert '{:}'.format(e) == "€ 1.99"
    assert '{:f}'.format(e) == "€ 1.99"
    assert '{:.5}'.format(e) == "€ 1.9900"
    assert '{:.5f}'.format(e) == "€ 1.99000"
    assert '{:.20}'.format(e) == "€ {:.20}".format(d)
    assert '{:.20f}'.format(e) == "€ {:.20f}".format(d)


def test_add():
    Money = MoneyMaker()
    assert Money('1.23') + Money(2) == Money('3.23')
    assert Money('1.23') + Money(0) == Money('1.23')
    assert Money(1) + (Money(-1)) == Money(0)
    assert Money(1).__radd__(Money(2)) == Money(3)


def test_add_zero():
    Money = MoneyMaker()
    assert Money('1.23') + 0 == Money('1.23')
    assert Money('1.23') + 0.0 == Money('1.23')
    assert Money('1.23') + Money('NaN') == Money('1.23')
    assert 0 + Money('1.23') == Money('1.23')
    assert 0.0 + Money('1.23') == Money('1.23')
    assert Money('NaN') + Money('1.23') == Money('1.23')
    with pytest.raises(ValueError):
        Money(1) + 1
    with pytest.raises(ValueError):
        Money(1) + 1.0
    with pytest.raises(ValueError):
        1 + Money(1)
    with pytest.raises(ValueError):
        1.0 + Money(1)


def test_sub():
    Money = MoneyMaker()
    assert Money(1) - Money(2) == Money(-1)
    with pytest.raises(ValueError):
        Money(1).__rsub__(Money(2))


def test_neg():
    Money = MoneyMaker()
    assert -Money(1) == Money(-1)
    assert -Money(-1) == Money(1)
    assert -Money(0) == Money(0)


def test_mul():
    Money = MoneyMaker()
    assert Money(1) * 1 == Money(1)
    assert Money(1) * 0 == Money(0)
    assert Money(1) * -1 == Money(-1)
    assert Money(1) * 1 == Money(1)
    assert Money(1) * 0 == Money(0)
    assert Money(1).__rmul__(-1) == Money(-1)
    assert Money(1).__rmul__(1.0) == Money(1)
    assert format(Money(1) * None) == "€ –"
    with pytest.raises(ValueError):
        Money(1) * (Money(1))


def test_div():
    Money = MoneyMaker()
    assert Money(1) / 2, Money(0.5)
    assert Money(1) / 2.0, Money(0.5)
    with pytest.raises(ValueError):
        Money(1) / Money(2)
    with pytest.raises(ValueError):
        Money(1).__rdiv__(2)


def test_truediv():
    Money = MoneyMaker()
    assert Money(1).__truediv__(2) == Money(0.5)
    assert Money(1).__truediv__(2.0) == Money(0.5)
    with pytest.raises(ValueError):
        Money(1).__truediv__(Money(2))
    with pytest.raises(ValueError):
        Money(1).__rtruediv__(2)


def test_pow():
    Money = MoneyMaker()
    with pytest.raises(ValueError):
        Money(1) ** Money(2)


def test_float():
    Money = MoneyMaker()
    money = Money(Decimal('sNaN'))
    with pytest.raises(ValueError):
        float(money)
    money = Money(Decimal('NaN'))
    assert math.isnan(float(money)) is True
    money = Money(Decimal('-NaN'))
    assert math.isnan(float(money)) is True
    money = Money(Decimal('1.0'))
    assert float(money) == 1.0


def test_currency():
    assert EUR.currency == 'EUR'
    assert EUR.subunits == 100
    JPY = MoneyMaker('JPY')
    assert JPY.currency == 'JPY'
    assert JPY.subunits == 1


def test_as_decimal():
    amount = EUR('1.23')
    quantized_decimal = Decimal('1.23').quantize(Decimal('.01'))
    assert amount.as_decimal() == quantized_decimal


def test_as_integer():
    assert EUR('1.23').as_integer() == 123


def test_as_bool():
    amount = EUR('1.23')
    assert bool(amount) is True
    amount = EUR(0)
    assert bool(amount) is False
    amount = EUR()
    assert bool(amount) is False


def test_pickle():
    amount = EUR('1.23')
    pickled = pickle.dumps(amount)
    assert pickle.loads(pickled) == amount


class MoneyTestSerializer(serializers.Serializer):
    amount = MoneyField(read_only=True)


def test_money_serializer():
    instance = type(str('TestMoney'), (object,), {'amount': EUR('1.23')})
    serializer = MoneyTestSerializer(instance)
    assert {'amount': '€ 1.23'} == serializer.data


def test_json_renderer():
    renderer = JSONRenderer()
    data = {'amount': EUR('1.23')}
    rendered_json = renderer.render(data, 'application/json')
    assert {'amount': "€ 1.23"} == json.loads(rendered_json.decode('utf-8'))
